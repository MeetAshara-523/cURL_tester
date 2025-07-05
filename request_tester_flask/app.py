import uuid
from flask import Flask, render_template, request, jsonify, render_template_string
from cURL import CurlConverter
import requests
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from method import run_iterations
from progressbar import start_background_task, get_task_progress

app = Flask(__name__)
tasks = {}


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        curl_command = request.form["curl_command"]
        expected_text = request.form["expected_text"]
        iterations = int(request.form["iterations"])
        max_workers = int(request.form.get("max_workers", 15))
        engine = request.form.get("engine", "requests")
        result = run_iterations(curl_command, expected_text, iterations, engine, max_workers)
        return jsonify(result)
    return render_template("index.html")


@app.route("/snippet", methods=["POST"])
def snippet():
    curl_command = request.form.get("curl_command", "").strip()
    expected_text = request.form.get("expected_text", "").strip()
    max_workers = int(request.form.get("max_workers", 15))
    engine = request.form.get("engine", "requests")

    try:
        method, url, headers, data, extra = CurlConverter(curl_command).convert()
    except Exception as e:
        return f"<h3>Error parsing cURL: {str(e)}</h3>"

    from engines import get_engine_import_code, get_engine_session_code, get_engine_request_code
    
    import_code = get_engine_import_code(engine)
    session_code = get_engine_session_code(engine)
    request_code = get_engine_request_code(engine, method, bool(data))

    # Handle aiohttp differently in snippet
    if engine == "aiohttp":
        code = f'''{import_code}
import time
from concurrent.futures import ThreadPoolExecutor

url = {repr(url)}
headers = {headers or '{}'}
{f"data = {repr(data)}" if data else ""}
expected_text = {repr(expected_text)}
max_workers = {max_workers}

print(f"Sending request with {{max_workers}} concurrent workers...")

async def make_single_request():
    async with aiohttp.ClientSession() as session:
        try:
            {'async with session.post(url, headers=headers, data=data) as response:' if method == 'POST' else 'async with session.get(url, headers=headers) as response:'}
                text = await response.text()
                return text, response.status
        except Exception as e:
            return None, str(e)

def run_sync_request():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(make_single_request())
    finally:
        loop.close()

start_time = time.time()

with ThreadPoolExecutor(max_workers=max_workers) as executor:
    future = executor.submit(run_sync_request)
    try:
        content, status = future.result()
        end_time = time.time()
        elapsed = end_time - start_time
        
        if content and expected_text.lower() in content.lower():
            print("✅ Found expected text!")
        else:
            print("❌ Expected text not found.")
            
        print(f"Response received in {{elapsed:.2f}} seconds")
        print(f"Status: {{status}}")
        
    except Exception as e:
        print("⚠️ Request failed:", str(e))
'''
    else:
        code = f'''{import_code}
import time
from concurrent.futures import ThreadPoolExecutor

url = {repr(url)}
headers = {headers or '{}'}
{f"data = {repr(data)}" if data else ""}
expected_text = {repr(expected_text)}
max_workers = {max_workers}

print(f"Sending request with {{max_workers}} concurrent workers...")

{session_code}

def make_single_request():
    try:
        {request_code}
        return response.text, response.status_code
    except Exception as e:
        return None, str(e)

start_time = time.time()

with ThreadPoolExecutor(max_workers=max_workers) as executor:
    future = executor.submit(make_single_request)
    try:
        content, status_code = future.result()
        end_time = time.time()
        elapsed = end_time - start_time

        print("Status Code:", status_code)

        if content and expected_text.lower() in content.lower():
            print("✅ Found expected text!")
        else:
            print("❌ Expected text not found.")

        print(f"Response received in {{elapsed:.2f}} seconds")

    except Exception as e:
        print("⚠️ Request failed:", str(e))
    finally:
        if hasattr({'client' if engine == 'httpx' else 'session'}, 'close'):
            {'client' if engine == 'httpx' else 'session'}.close()
'''

    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
    <title>Generated Python Snippet</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/atom-one-dark.min.css" rel="stylesheet">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
    <script>hljs.highlightAll();</script>
    <style>
        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            font-family: 'Segoe UI', sans-serif;
            padding: 20px;
            min-height: 100vh;
        }
        .container {
            max-width: 1000px;
            margin: 0 auto;
        }
        .code-container {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.2);
        }
        pre {
            padding: 20px;
            border-radius: 12px;
            background: #282c34 !important;
            border: none;
            font-size: 14px;
            line-height: 1.6;
            overflow-x: auto;
        }
        .copy-btn {
            position: absolute;
            top: 15px;
            right: 20px;
            background: rgba(255,255,255,0.9);
            border: none;
            border-radius: 8px;
            padding: 8px 16px;
            font-size: 12px;
            font-weight: 500;
            color: #333;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        .copy-btn:hover {
            background: rgba(255,255,255,1);
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
            color: white;
        }
        .header h2 {
            font-weight: 700;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        .info-badge {
            background: rgba(255,255,255,0.2);
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 12px;
            margin: 0 5px;
            backdrop-filter: blur(5px);
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>🐍 Generated Python Snippet</h2>
            <span class="info-badge">{{ engine.upper() }}</span>
            <span class="info-badge">{{ max_workers }} Workers</span>
        </div>
        
        <div class="code-container">
            <div class="position-relative">
                <button class="copy-btn" onclick="copyToClipboard()">
                    <i class="fas fa-copy"></i> Copy Code
                </button>
                <pre><code class="language-python" id="codeBlock">{{ code }}</code></pre>
            </div>
        </div>
    </div>

    <script>
        function copyToClipboard() {
            const text = document.getElementById("codeBlock").innerText;
            navigator.clipboard.writeText(text).then(() => {
                const btn = document.querySelector('.copy-btn');
                const originalText = btn.innerHTML;
                btn.innerHTML = '✅ Copied!';
                btn.style.background = '#4CAF50';
                btn.style.color = 'white';
                setTimeout(() => {
                    btn.innerHTML = originalText;
                    btn.style.background = 'rgba(255,255,255,0.9)';
                    btn.style.color = '#333';
                }, 2000);
            });
        }
    </script>
</body>
</html>
""", code=code, engine=engine, max_workers=max_workers)

@app.route("/start_task", methods=["POST"])
def start_task():
    curl_command = request.form["curl_command"]
    expected_text = request.form["expected_text"]
    iterations = int(request.form["iterations"])
    max_workers = int(request.form.get("max_workers", 10))
    engine = request.form.get("engine", "requests")
    task_id = start_background_task(curl_command, expected_text, iterations, engine, max_workers)
    return jsonify({"task_id": task_id})


@app.route("/progress/<task_id>")
def progress(task_id):
    task = get_task_progress(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    resp = {
        "done": task["done"],
        "total": task["total"],
        "results": task.get("results", []),
        "summary": task.get("summary", {}),
        "finished": task.get("finished", False),
        "time": task.get("time", "0.00 seconds")
    }
    return jsonify(resp)


if __name__ == "__main__":
    app.run(debug=True)