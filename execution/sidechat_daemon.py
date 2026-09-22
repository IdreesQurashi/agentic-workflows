#!/usr/bin/env python3
import os
import json
import glob
import urllib.request
import urllib.error
from http.server import HTTPServer, BaseHTTPRequestHandler

KEY_POOL_FILE = "/home/idrees/Raw various data/job_agent/gemini_keys_pool.json"

def get_gemini_key():
    if os.path.exists(KEY_POOL_FILE):
        try:
            with open(KEY_POOL_FILE, "r") as f:
                pool = json.load(f)
            keys = pool.get("active_keys", [])
            if not keys:
                return ""
            idx = pool.get("current_index", 0)
            key = keys[idx % len(keys)]
            
            # Rotate
            pool["current_index"] = (idx + 1) % len(keys)
            try:
                with open(KEY_POOL_FILE, "w") as f:
                    json.dump(pool, f, indent=2)
            except Exception:
                pass
            return key
        except Exception:
            pass
    return os.environ.get("GEMINI_API_KEY", "")

def generate_content(prompt_text, image_b64=None):
    key = get_gemini_key()
    if not key:
        return "Error: No API key found in pool."
        
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-lite-latest:generateContent?key={key}"
    
    parts = [{"text": prompt_text}]
    if image_b64:
        if "," in image_b64:
            mime_part, b64_data = image_b64.split(",", 1)
            mime_type = mime_part.split(":")[1].split(";")[0]
        else:
            b64_data = image_b64
            mime_type = "image/jpeg"
            
        parts.append({
            "inline_data": {
                "mime_type": mime_type,
                "data": b64_data
            }
        })
        
    payload = {
        "contents": [{"parts": parts}]
    }
    
    req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req) as response:
            res_data = json.loads(response.read().decode('utf-8'))
            return res_data['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        return f"API Error: {str(e)}"

def get_latest_transcript_path():
    brain_dir = os.path.expanduser("~/.gemini/antigravity/brain")
    if not os.path.exists(brain_dir):
        return None
    pattern = os.path.join(brain_dir, "*", ".system_generated", "logs", "transcript.jsonl")
    transcripts = glob.glob(pattern)
    if not transcripts:
        return None
    transcripts.sort(key=os.path.getmtime, reverse=True)
    return transcripts[0]

def build_context():
    transcript_path = get_latest_transcript_path()
    if not transcript_path:
        return ""
    
    history = []
    try:
        with open(transcript_path, "r") as f:
            for line in f:
                if not line.strip(): continue
                data = json.loads(line)
                step_type = data.get("type", "")
                content = data.get("content", "")
                
                if step_type == "USER_INPUT":
                    history.append(f"User: {content}")
                elif step_type == "PLANNER_RESPONSE":
                    history.append(f"Agent: {content}")
    except Exception:
        return ""
        
    return "\n\n".join(history[-30:])

class SidechatHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            
            html_content = """<!DOCTYPE html>
<html>
<head>
    <title>Antigravity Multimodal Sidechat</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; margin: 0; padding: 15px; background: #1e1e1e; color: #d4d4d4; }
        #chat-container { display: flex; flex-direction: column; height: 92vh; }
        #messages { flex-grow: 1; overflow-y: auto; padding: 15px; border: 1px solid #333; border-radius: 8px; margin-bottom: 15px; background: #252526; }
        .msg { margin-bottom: 20px; font-size: 14px; line-height: 1.5; }
        .msg.user { color: #9cdcfe; }
        .msg.bot { color: #ce9178; }
        .msg-content { white-space: pre-wrap; margin-top: 5px; }
        .msg-img { max-width: 200px; max-height: 200px; display: block; margin-top: 10px; border-radius: 4px; border: 1px solid #444; }
        
        #preview-container { display: none; margin-bottom: 10px; position: relative; width: max-content; }
        #preview-img { max-height: 100px; border-radius: 4px; border: 1px solid #555; }
        #preview-clear { position: absolute; top: -8px; right: -8px; background: #c53030; color: white; border: none; border-radius: 50%; width: 22px; height: 22px; cursor: pointer; font-size: 12px; line-height: 20px; padding: 0; text-align: center; }
        
        #input-area { display: flex; flex-direction: column; }
        #input-row { display: flex; }
        #input-row input { flex-grow: 1; padding: 12px; border: 1px solid #333; border-radius: 8px; background: #3c3c3c; color: white; outline: none; font-size: 14px; }
        #input-row button { padding: 12px 20px; margin-left: 10px; border: none; border-radius: 8px; background: #0e639c; color: white; cursor: pointer; font-weight: bold; }
        #input-row button:hover { background: #1177bb; }
        #input-row button:disabled { background: #555; cursor: not-allowed; }
        .hint { font-size: 11px; color: #888; margin-top: 5px; text-align: center; }
    </style>
</head>
<body>
    <div id="chat-container">
        <div id="messages"></div>
        <div id="input-area">
            <div id="preview-container">
                <img id="preview-img" src="" />
                <button id="preview-clear" onclick="clearPreview()">X</button>
            </div>
            <div id="input-row">
                <input type="text" id="question" placeholder="Ask anything or paste an image (Ctrl+V)..." onkeypress="handleKey(event)" />
                <button id="send-btn" onclick="sendQuestion()">Send</button>
            </div>
            <div class="hint">Supports text and image pasting. Acts as a general LLM with awareness of your active workspace.</div>
        </div>
    </div>
    <script>
        let currentImageB64 = null;
        
        document.addEventListener('paste', (e) => {
            const items = (e.clipboardData || e.originalEvent.clipboardData).items;
            for (let index in items) {
                const item = items[index];
                if (item.kind === 'file' && item.type.includes('image/')) {
                    const blob = item.getAsFile();
                    const reader = new FileReader();
                    reader.onload = (event) => {
                        currentImageB64 = event.target.result;
                        document.getElementById('preview-img').src = currentImageB64;
                        document.getElementById('preview-container').style.display = 'block';
                        document.getElementById('question').focus();
                    };
                    reader.readAsDataURL(blob);
                    e.preventDefault();
                }
            }
        });

        function clearPreview() {
            currentImageB64 = null;
            document.getElementById('preview-container').style.display = 'none';
            document.getElementById('preview-img').src = '';
            document.getElementById('question').focus();
        }

        function handleKey(e) { if(e.key === 'Enter') sendQuestion(); }
        
        async function sendQuestion() {
            const qInput = document.getElementById('question');
            const btn = document.getElementById('send-btn');
            const q = qInput.value.trim();
            
            if(!q && !currentImageB64) return;
            
            addMessage('User', q, 'user', currentImageB64);
            
            const payloadImage = currentImageB64;
            qInput.value = '';
            clearPreview();
            
            qInput.disabled = true;
            btn.disabled = true;
            
            try {
                const res = await fetch('/ask', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ question: q, image: payloadImage })
                });
                const data = await res.json();
                addMessage('Sidekick', data.answer, 'bot', null);
            } catch(e) {
                addMessage('System', 'Error: ' + e, 'bot', null);
            }
            
            qInput.disabled = false;
            btn.disabled = false;
            qInput.focus();
        }
        
        function addMessage(sender, text, cls, imgSrc) {
            const msgs = document.getElementById('messages');
            const div = document.createElement('div');
            div.className = 'msg ' + cls;
            
            let imgHtml = '';
            if(imgSrc) {
                imgHtml = `<img src="${imgSrc}" class="msg-img" />`;
            }
            
            div.innerHTML = `<strong>${sender}</strong>${imgHtml}<div class="msg-content">${text}</div>`;
            msgs.appendChild(div);
            msgs.scrollTop = msgs.scrollHeight;
        }
        addMessage('System', 'Multimodal LLM active. Paste images anywhere on this page.', 'bot');
    </script>
</body>
</html>"""
            self.wfile.write(html_content.encode('utf-8'))
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path == "/ask":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            question = data.get("question", "")
            image_b64 = data.get("image", None)
            
            context = build_context()
            
            prompt = (
                "You are a highly capable AI assistant helping Idrees. You act as a normal, general purpose LLM. "
                "You have access to the recent conversation history of his primary IDE chat below for awareness, "
                "but you should answer his questions normally and directly. DO NOT explicitly state that you are reading from context unless strictly necessary.\\n\\n"
            )
            
            if context:
                prompt += f"--- BACKGROUND IDE CONTEXT ---\\n{context}\\n--- END CONTEXT ---\\n\\n"
                
            prompt += f"User Question: {question}"
            
            try:
                answer = generate_content(prompt, image_b64)
            except Exception as e:
                answer = f"Error generating answer: {e}"
                
            response_data = {"answer": answer}
            
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(response_data).encode('utf-8'))
        else:
            self.send_error(404)

def run(server_class=HTTPServer, handler_class=SidechatHandler, port=8044):
    server_address = ('127.0.0.1', port)
    httpd = server_class(server_address, handler_class)
    print(f"Starting Multimodal Sidechat Daemon on http://127.0.0.1:{port}")
    httpd.serve_forever()

if __name__ == "__main__":
    run()
