import urllib.request
import urllib.parse
import re
from html.parser import HTMLParser

class DDGParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.results = []
        self.current_title = None
        self.current_href = None
        self.in_result = False
        self.in_snippet = False
        self.snippet = ""

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if tag == 'a' and 'result__url' in attrs_dict.get('class', ''):
            self.in_result = True
            self.current_href = attrs_dict.get('href', '')
        elif tag == 'a' and 'result__snippet' in attrs_dict.get('class', ''):
            self.in_snippet = True
            self.snippet = ""

    def handle_endtag(self, tag):
        if tag == 'a' and self.in_result:
            self.in_result = False
        elif tag == 'a' and self.in_snippet:
            self.in_snippet = False
            self.results.append((self.current_href, self.snippet))

    def handle_data(self, data):
        if self.in_snippet:
            self.snippet += data

query = "medspas medical spa aesthetics Abbeville Louisiana"
url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"

req = urllib.request.Request(
    url,
    headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
)

try:
    with urllib.request.urlopen(req) as resp:
        html_content = resp.read().decode('utf-8')
        # Simple regex extraction for DDG html results
        # DDG html structure usually has <a class="result__snippet" ...>text</a> and <a class="result__url" ...>url</a>
        snippets = re.findall(r'<a class="result__snippet"[^>]*>(.*?)</a>', html_content, re.DOTALL)
        titles = re.findall(r'<a class="result__a"[^>]*>(.*?)</a>', html_content, re.DOTALL)
        urls = re.findall(r'<a class="result__url"[^>]*href="([^"]+)"', html_content)

        print(f"Found {len(titles)} titles, {len(urls)} urls, {len(snippets)} snippets.")
        for i in range(min(len(titles), len(snippets))):
            clean_title = re.sub(r'<[^>]+>', '', titles[i])
            clean_snippet = re.sub(r'<[^>]+>', '', snippets[i])
            print(f"\n--- Result {i+1} ---")
            print(f"Title: {clean_title}")
            print(f"Snippet: {clean_snippet}")
            if i < len(urls):
                print(f"URL: {urls[i]}")
except Exception as e:
    print(f"Error searching DDG: {e}")
