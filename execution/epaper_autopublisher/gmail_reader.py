import imaplib
import email
from email.header import decode_header
import re
from datetime import datetime, timezone, timedelta

class GmailReader:
    def __init__(self, imap_server: str, imap_port: int, email_addr: str, app_password: str, sender_filter: str):
        self.imap_server = imap_server
        self.imap_port = imap_port
        self.email_addr = email_addr
        self.app_password = app_password
        self.sender_filter = sender_filter.lower()

    def connect(self):
        mail = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
        mail.login(self.email_addr, self.app_password)
        return mail

    def decode_mime_words(self, s: str) -> str:
        if not s:
            return ""
        decoded_fragments = decode_header(s)
        text = ""
        for frag, enc in decoded_fragments:
            if isinstance(frag, bytes):
                text += frag.decode(enc or "utf-8", errors="replace")
            else:
                text += str(frag)
        return text

    def fetch_recent_newspaper_emails(self, max_emails: int = 8) -> list:
        mail = self.connect()
        mail.select("INBOX")
        
        status, data = mail.search(None, f'(FROM "{self.sender_filter}")')
        if status != "OK" or not data[0]:
            # Try searching all unread
            status, data = mail.search(None, "UNSEEN")
            if status != "OK" or not data[0]:
                mail.logout()
                return []

        msg_ids = data[0].split()[-max_emails:]
        total_msgs = len(msg_ids)
        print(f"[*] Found {total_msgs} recent emails. Fetching content...")
        bundles = []

        for idx, msg_id in enumerate(reversed(msg_ids), start=1):
            print(f"    [{idx}/{total_msgs}] Downloading email ID {msg_id.decode()}...")
            res, msg_data = mail.fetch(msg_id, "(RFC822)")
            if res != "OK":
                continue
                
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    subject = self.decode_mime_words(msg.get("Subject", ""))
                    from_addr = self.decode_mime_words(msg.get("From", ""))
                    date_hdr = msg.get("Date", "")
                    
                    attachments = []
                    body_text = ""
                    
                    if msg.is_multipart():
                        for part in msg.walk():
                            content_disposition = str(part.get("Content-Disposition", ""))
                            content_type = part.get_content_type()
                            filename = part.get_filename()
                            
                            if filename:
                                filename = self.decode_mime_words(filename)
                                file_bytes = part.get_payload(decode=True)
                                attachments.append({
                                    "filename": filename,
                                    "data": file_bytes,
                                    "mime_type": content_type
                                })
                            elif content_type in ["text/plain", "text/html"] and not body_text:
                                payload = part.get_payload(decode=True)
                                if payload:
                                    body_text = payload.decode(errors="replace")[:300]
                    else:
                        payload = msg.get_payload(decode=True)
                        if payload:
                            body_text = payload.decode(errors="replace")[:300]

                    bundles.append({
                        "msg_id": msg_id.decode() if isinstance(msg_id, bytes) else str(msg_id),
                        "from": from_addr,
                        "subject": subject,
                        "snippet": body_text[:200],
                        "date": date_hdr,
                        "attachments": attachments
                    })

        mail.logout()
        return bundles

    @staticmethod
    def partition_and_aggregate(email_bundles: list, publications_cfg: dict) -> dict:
        """
        Partitions multi-email batches, deduplicates pages naturally by page number
        (keeping the newest version if an editor re-sends a page), and combines all
        pages into strictly ONE post collection per publication, sorted in ascending order.
        """
        result = {
            "pukkar": [],
            "kashmir_times": []
        }

        pukkar_keywords = [k.lower() for k in publications_cfg.get("pukkar", {}).get("keywords", ["pukk", "azadi"])]
        pukkar_expected = publications_cfg.get("pukkar", {}).get("expected_pages", 4)
        kt_expected = publications_cfg.get("kashmir_times", {}).get("expected_pages", 8)

        def get_page_num(fn: str, is_pukkar: bool) -> int:
            fn_low = fn.lower()
            default_back = pukkar_expected if is_pukkar else kt_expected
            if "fp" in fn_low or "front" in fn_low:
                return 1
            if "bak" in fn_low or "back" in fn_low:
                return default_back
            m = re.search(r"p?(\d+)", fn_low)
            return int(m.group(1)) if m else 999

        pages_by_pub = {
            "pukkar": {},
            "kashmir_times": {}
        }

        # Iterate through bundles (newest first). First encounter of page number is kept.
        for bundle in email_bundles:
            sub = bundle.get("subject", "").lower()
            snip = bundle.get("snippet", "").lower()
            combined_text = f"{sub} {snip}"
            
            is_pukkar = any(k in combined_text for k in pukkar_keywords)
            target_key = "pukkar" if is_pukkar else "kashmir_times"
            
            for att in bundle.get("attachments", []):
                fn = att.get("filename", "")
                if any(fn.lower().endswith(ext) for ext in [".jpg", ".jpeg", ".png", ".webp"]):
                    pnum = get_page_num(fn, is_pukkar)
                    if pnum not in pages_by_pub[target_key]:
                        pages_by_pub[target_key][pnum] = att

        for pub_key in result:
            sorted_nums = sorted(pages_by_pub[pub_key].keys())
            result[pub_key] = [pages_by_pub[pub_key][n] for n in sorted_nums]

        return result

    @staticmethod
    def generate_dummy_bundles() -> list:
        """
        Generates realistic multi-batch dummy emails simulating the exact scenario:
        - Pukkar arrives as 2 emails (2 pages each = 4 total)
        - Kashmir Times arrives as 4 emails (2 pages each = 8 total)
        """
        # Minimal valid 1x1 JPEG bytes for testing
        dummy_jpeg = (
            b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00`\x00`\x00\x00'
            b'\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t'
            b'\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a'
            b'\x1f\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342'
            b'\xff\xc0\x00\x0b\x08\x00\x01\x00\x01\x01\x01\x11\x00\xff\xc4'
            b'\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00'
            b'\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b'
            b'\xff\xda\x00\x08\x01\x01\x00\x00?\x00\xbf\x00\xff\xd9'
        )

        bundles = [
            # Pukkar Batch 1: Pages 1 & 2
            {
                "msg_id": "dummy_pukkar_1",
                "from": "Daily Pukkar <dailykashmirtimes.ib@gmail.com>",
                "subject": "Daily Pukkar-e-Azadi - Pages 1 to 2",
                "snippet": "Attached are pages 1 and 2 for today edition of Pukkar.",
                "date": "Fri, 02 Oct 2026 21:00:00 +0500",
                "attachments": [
                    {"filename": "p1-10.jpg", "data": dummy_jpeg, "mime_type": "image/jpeg"},
                    {"filename": "p2-10.jpg", "data": dummy_jpeg, "mime_type": "image/jpeg"}
                ]
            },
            # Pukkar Batch 2: Pages 3 & 4
            {
                "msg_id": "dummy_pukkar_2",
                "from": "Daily Pukkar <dailykashmirtimes.ib@gmail.com>",
                "subject": "Daily Pukkar-e-Azadi - Pages 3 to 4",
                "snippet": "Attached are remaining pages 3 and 4 for Pukkar.",
                "date": "Fri, 02 Oct 2026 21:01:00 +0500",
                "attachments": [
                    {"filename": "p3-10.jpg", "data": dummy_jpeg, "mime_type": "image/jpeg"},
                    {"filename": "p4-10.jpg", "data": dummy_jpeg, "mime_type": "image/jpeg"}
                ]
            },
            # Kashmir Times Batch 1: Pages 1 & 2
            {
                "msg_id": "dummy_kt_1",
                "from": "Daily Kashmir Times <dailykashmirtimes.ib@gmail.com>",
                "subject": "Kashmir Times Edition Pages 1 and 2",
                "snippet": "Kashmir Times daily issue part 1",
                "date": "Fri, 02 Oct 2026 21:05:00 +0500",
                "attachments": [
                    {"filename": "p1 (1).jpg", "data": dummy_jpeg, "mime_type": "image/jpeg"},
                    {"filename": "p2 (1).jpg", "data": dummy_jpeg, "mime_type": "image/jpeg"}
                ]
            },
            # Kashmir Times Batch 2: Pages 3 & 4
            {
                "msg_id": "dummy_kt_2",
                "from": "Daily Kashmir Times <dailykashmirtimes.ib@gmail.com>",
                "subject": "Kashmir Times Edition Pages 3 and 4",
                "snippet": "Kashmir Times daily issue part 2",
                "date": "Fri, 02 Oct 2026 21:06:00 +0500",
                "attachments": [
                    {"filename": "p3 (1).jpg", "data": dummy_jpeg, "mime_type": "image/jpeg"},
                    {"filename": "p4 (1).jpg", "data": dummy_jpeg, "mime_type": "image/jpeg"}
                ]
            },
            # Kashmir Times Batch 3: Pages 5 & 6
            {
                "msg_id": "dummy_kt_3",
                "from": "Daily Kashmir Times <dailykashmirtimes.ib@gmail.com>",
                "subject": "Kashmir Times Edition Pages 5 and 6",
                "snippet": "Kashmir Times daily issue part 3",
                "date": "Fri, 02 Oct 2026 21:07:00 +0500",
                "attachments": [
                    {"filename": "p5 (1).jpg", "data": dummy_jpeg, "mime_type": "image/jpeg"},
                    {"filename": "p6 (1).jpg", "data": dummy_jpeg, "mime_type": "image/jpeg"}
                ]
            },
            # Kashmir Times Batch 4: Pages 7 & 8
            {
                "msg_id": "dummy_kt_4",
                "from": "Daily Kashmir Times <dailykashmirtimes.ib@gmail.com>",
                "subject": "Kashmir Times Edition Pages 7 and 8",
                "snippet": "Kashmir Times daily issue part 4 final",
                "date": "Fri, 02 Oct 2026 21:08:00 +0500",
                "attachments": [
                    {"filename": "p7 (1).jpg", "data": dummy_jpeg, "mime_type": "image/jpeg"},
                    {"filename": "p8 (1).jpg", "data": dummy_jpeg, "mime_type": "image/jpeg"}
                ]
            }
        ]

        return bundles
