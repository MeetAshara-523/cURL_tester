import time
from concurrent.futures import ThreadPoolExecutor
from cURL import CurlConverter
from engines import RequestEngine

def run_iterations(curl_command, expected_text, iterations, engine="requests", max_workers=10):
    try:
        method, url, headers, data, json_data = CurlConverter(curl_command).convert()
    except Exception as e:
        return {"error": str(e)}

    results = []
    summary = {"success": 0, "fail": 0, "found": 0, "total": iterations}
    
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
                return f"✅ Iteration {i}: Found at index {idx}\n...{preview}..."
            else:
                summary["fail"] += 1
                return f"❌ Iteration {i}: Not Found (Status {status_code})"
        except Exception as e:
            summary["fail"] += 1
            return f"⚠️ Iteration {i}: ERROR - {str(e)}"
        finally:
            request_engine.close()

    start = time.time()
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(send_request, i) for i in range(1, iterations + 1)]
        for f in futures:
            results.append(f.result())
    total_time = time.time() - start

    return {
        "results": results,
        "summary": summary,
        "time": f"{total_time:.2f} seconds"
    }