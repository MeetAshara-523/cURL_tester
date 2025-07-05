import uuid
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from cURL import CurlConverter
from engines import RequestEngine

tasks = {}

def start_background_task(curl_command, expected_text, iterations, engine="requests", max_workers=10):
    task_id = str(uuid.uuid4())
    tasks[task_id] = {
        "done": 0,
        "total": iterations,
        "results": [],
        "summary": {"success": 0, "fail": 0, "found": 0, "total": iterations},
        "finished": False,
        "time": "0.00 seconds",
        "max_workers": max_workers
    }

    def run_task():
        try:
            method, url, headers, data, json_data = CurlConverter(curl_command).convert()
        except Exception as e:
            tasks[task_id]["error"] = str(e)
            tasks[task_id]["finished"] = True
            return

        summary = tasks[task_id]["summary"]
        results = tasks[task_id]["results"]
        start = time.time()
        
        def send_request(i):
            nonlocal summary
            request_engine = RequestEngine(engine)
            try:
                content, status_code = request_engine.make_request(method, url, headers, data, json_data)
                if expected_text.lower() in content.lower():
                    summary["success"] += 1
                    summary["found"] += 1
                    idx = content.lower().find(expected_text.lower())
                    preview = content[max(0, idx - 30): idx + len(expected_text) + 30]
                    result = f"✅ Iteration {i}: Found at index {idx}\n...{preview}..."
                else:
                    summary["fail"] += 1
                    result = f"❌ Iteration {i}: Not Found (Status {status_code})"
            except Exception as e:
                summary["fail"] += 1
                result = f"⚠️ Iteration {i}: ERROR - {str(e)}"
            finally:
                request_engine.close()
            
            # Update progress
            tasks[task_id]["done"] += 1
            results.append(result)
            return result

        # Use ThreadPoolExecutor for concurrent execution
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(send_request, i) for i in range(1, iterations + 1)]
            for future in futures:
                future.result()  # Wait for completion

        total_time = time.time() - start
        tasks[task_id]["finished"] = True
        tasks[task_id]["time"] = f"{total_time:.2f} seconds"

    threading.Thread(target=run_task).start()
    return task_id

def get_task_progress(task_id):
    return tasks.get(task_id)