import urllib.request
import urllib.parse
import re

query = "medical spa medspa Abbeville LA skin care aesthetics"
url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"

req = urllib.request.Request(
    url,
    headers={
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/119.0'
    }
)

try:
    with urllib.request.urlopen(req) as resp:
        html = resp.read().decode('utf-8')
        # Find all result links and snippets
        # DDG html results are typically inside <div class="result"> ... <a class="result__url" ...> ... <a class="result__snippet" ...>
        results = re.findall(r'<div class="result[^"]*">.*?</div>\s*</div>', html, re.DOTALL)
        print(f"Found {len(results)} result blocks.")

        for idx, res in enumerate(results):
            title_match = re.search(r'<a class="result__a"[^>]*>(.*?)</a>', res, re.DOTALL)
            snippet_match = re.search(r'<a class="result__snippet"[^>]*>(.*?)</a>', res, re.DOTALL)
            url_match = re.search(r'<a class="result__url"[^>]*href="([^"]+)"', res)

            title = re.sub(r'<[^>]+>', '', title_match.group(1)) if title_match else "No title"
            snippet = re.sub(r'<[^>]+>', '', snippet_match.group(1)) if snippet_match else "No snippet"
            link = url_match.group(1) if url_match else "No link"

            print(f"\n[{idx+1}] {title.strip()}")
            print(f"URL: {link.strip()}")
            print(f"Snippet: {snippet.strip()}")

        if not results:
            # Fallback: print all links containing http
            links = re.findall(r'href="(https?://[^"]+)"', html)
            print("All links found:", links[:20])

except Exception as e:
    print(f"Error: {e}")
