import smtplib
import imaplib
import email
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import os
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("GmailEngine")

SENDER_EMAIL = "idreesqurashi6@gmail.com"
APP_PASSWORD = "qdrg poyy wvsi lgcn"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
IMAP_SERVER = "imap.gmail.com"
DEFAULT_CV = "/home/idrees/Documents/Idrees_Qurashi_CV.pdf"

@mcp.tool()
def check_recent_emails(max_count: int = 5) -> str:
    """Check the most recent emails in your Gmail inbox to monitor client or employer responses."""
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(SENDER_EMAIL, APP_PASSWORD)
        mail.select("inbox")
        status, data = mail.search(None, "ALL")
        if status != "OK" or not data[0]:
            mail.logout()
            return "Inbox empty or could not retrieve messages."
            
        msg_ids = data[0].split()[-max_count:]
        output = [f"=== Latest {len(msg_ids)} Emails in Gmail Inbox ==="]
        
        for msg_id in reversed(msg_ids):
            res, msg_data = mail.fetch(msg_id, "(RFC822)")
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    subject = msg.get("Subject", "No Subject")
                    from_addr = msg.get("From", "Unknown")
                    date_str = msg.get("Date", "")
                    output.append(f"• From: {from_addr}\n  Subject: {subject}\n  Date: {date_str}\n")
                    
        mail.logout()
        return "\n".join(output)
    except Exception as e:
        return f"IMAP Error checking emails: {e}"

@mcp.tool()
def send_bespoke_email(recipient: str, subject: str, body: str, attach_cv: bool = True) -> str:
    """Send a bespoke email from your Gmail account with optional CV attachment upon explicit user instruction."""
    try:
        msg = MIMEMultipart()
        msg["From"] = f"Idrees Qurashi <{SENDER_EMAIL}>"
        msg["To"] = recipient
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))
        
        if attach_cv and os.path.exists(DEFAULT_CV):
            with open(DEFAULT_CV, "rb") as f:
                part = MIMEApplication(f.read(), Name="Idrees_Qurashi_CV.pdf")
            part["Content-Disposition"] = 'attachment; filename="Idrees_Qurashi_CV.pdf"'
            msg.attach(part)
            
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=15)
        server.starttls()
        server.login(SENDER_EMAIL, APP_PASSWORD)
        server.send_message(msg)
        server.quit()
        return f"Email successfully sent to {recipient} with subject '{subject}'."
    except Exception as e:
        return f"SMTP Error sending email: {e}"

if __name__ == "__main__":
    mcp.run()
