import requests
import time
import re
import json

class WordPressClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
            "iwc-api-key": self.api_key
        }

    def check_connection(self) -> dict:
        url = f"{self.base_url}/wp-json/wp/v2/users/me"
        try:
            r = requests.get(url, headers=self.headers, timeout=15)
            if r.status_code == 200:
                data = r.json()
                return {"success": True, "user": data.get("name", "Unknown"), "id": data.get("id")}
            return {"success": False, "status": r.status_code, "error": r.text[:200]}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def upload_media(self, filename: str, file_bytes: bytes, mime_type: str = "image/jpeg") -> dict:
        url = f"{self.base_url}/wp-json/wp/v2/media"
        files = {
            "file": (filename, file_bytes, mime_type)
        }
        r = requests.post(url, headers=self.headers, files=files, timeout=60)
        if r.status_code in [200, 201]:
            data = r.json()
            mid = data.get("id") or data.get("ID")
            f_rel = data.get("file")
            surl = data.get("source_url") or (f"{self.base_url}/wp-content/uploads/{f_rel}" if f_rel else None)
            return {
                "success": True,
                "id": mid,
                "source_url": surl,
                "filename": filename
            }
        return {"success": False, "status": r.status_code, "error": r.text[:300]}

    def find_post_by_title(self, title: str, category_id: int = 42) -> int:
        url = f"{self.base_url}/wp-json/wp/v2/posts?search={title}&categories={category_id}"
        try:
            r = requests.get(url, headers=self.headers, timeout=15)
            if r.status_code == 200:
                posts = r.json()
                for p in posts:
                    if p.get("title", {}).get("rendered", "") == title:
                        return p.get("id")
        except Exception:
            pass
        return None

    def create_dearflip_post(self, title: str, pages: list, category_id: int = 42, author_id: int = 1) -> dict:
        if not pages:
            return {"success": False, "error": "Cannot create post with zero pages"}

        def natural_sort_key(p):
            fn = p.get("filename", "")
            match = re.search(r"p?(\d+)", fn.lower())
            return int(match.group(1)) if match else 999

        sorted_pages = sorted(pages, key=natural_sort_key)
        
        first_page = sorted_pages[0]
        featured_media_id = first_page.get("id")
        thumb_url = first_page.get("source_url")
        
        quoted_sources = [f'"{p["source_url"]}"' for p in sorted_pages if p.get("source_url")]
        sources_str = ",".join(quoted_sources)
        
        timestamp = int(time.time())
        
        content = (
            f'<div class="_df_book df-lite" id="df_{timestamp}" _slug="{title}" data-title="{title}" '
            f'wpoptions="true" thumb="{thumb_url}" thumbtype="" ></div>\n'
            f'<p><script class="df-shortcode-script" nowprocket type="application/javascript">'
            f'window.option_df_{timestamp} = {{"outline":[],"autoEnableOutline":"true","autoEnableThumbnail":"true",'
            f'"overwritePDFOutline":"false","direction":"1","pageSize":"0","maxTextureSize":"2048",'
            f'"source":[{sources_str}],"wpOptions":"true","links":[[],[],[],[],[]]}}; '
            f'if(window.DFLIP && window.DFLIP.parseBooks){{window.DFLIP.parseBooks();}}</script></p>'
        )

        payload = {
            "title": title,
            "content": content,
            "status": "publish",
            "categories": [category_id],
            "featured_media": featured_media_id,
            "author": author_id
        }

        existing_id = self.find_post_by_title(title, category_id)
        if existing_id:
            url = f"{self.base_url}/wp-json/wp/v2/posts/{existing_id}"
            action = "updated"
        else:
            url = f"{self.base_url}/wp-json/wp/v2/posts"
            action = "created"

        r = requests.post(url, headers=self.headers, json=payload, timeout=30)
        if r.status_code in [200, 201]:
            data = r.json()
            return {
                "success": True,
                "action": action,
                "post_id": data.get("id"),
                "link": data.get("link"),
                "pages_count": len(sorted_pages)
            }
        return {"success": False, "status": r.status_code, "error": r.text[:300]}
