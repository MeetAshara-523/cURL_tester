import requests
import time
from concurrent.futures import ThreadPoolExecutor

url = 'https://www.flipkart.com/audio-video/headset/pr?sid=0pm%2Cfcn&p%5B%5D=facets.connectivity%255B%255D%3DBluetooth&sort=popularity&p%5B%5D=facets.rating%255B%255D%3D3%25E2%2598%2585%2B%2526%2Babove&p%5B%5D=facets.rating%255B%255D%3D4%25E2%2598%2585%2B%2526%2Babove&p%5B%5D=facets.price_range.from%3D599&p%5B%5D=facets.price_range.to%3DMax&p%5B%5D=facets.headphone_type%255B%255D%3DTrue%2BWireless&param=86&hpid=WqCPtE2MbDEYEbYbttXC1qp7_Hsxr70nj65vMAAFKlc%3D&ctx=eyJjYXJkQ29udGV4dCI6eyJhdHRyaWJ1dGVzIjp7InZhbHVlQ2FsbG91dCI6eyJtdWx0aVZhbHVlZEF0dHJpYnV0ZSI6eyJrZXkiOiJ2YWx1ZUNhbGxvdXQiLCJpbmZlcmVuY2VUeXBlIjoiVkFMVUVfQ0FMTE9VVCIsInZhbHVlcyI6WyJHcmFiIE5vdyJdLCJ2YWx1ZVR5cGUiOiJNVUxUSV9WQUxVRUQifX0sImhlcm9QaWQiOnsic2luZ2xlVmFsdWVBdHRyaWJ1dGUiOnsia2V5IjoiaGVyb1BpZCIsImluZmVyZW5jZVR5cGUiOiJQSUQiLCJ2YWx1ZSI6IkFDQ0g1RktRUkdWMko4TkoiLCJ2YWx1ZVR5cGUiOiJTSU5HTEVfVkFMVUVEIn19LCJ0aXRsZSI6eyJtdWx0aVZhbHVlZEF0dHJpYnV0ZSI6eyJrZXkiOiJ0aXRsZSIsImluZmVyZW5jZVR5cGUiOiJUSVRMRSIsInZhbHVlcyI6WyJCZXN0IFRydWV3aXJlbGVzcyBIZWFkcGhvbmVzIl0sInZhbHVlVHlwZSI6Ik1VTFRJX1ZBTFVFRCJ9fX19fQ%3D%3D'
headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7', 'Accept-Language': 'en-US,en;q=0.9', 'Connection': 'keep-alive', 'Sec-Fetch-Dest': 'document', 'Sec-Fetch-Mode': 'navigate', 'Sec-Fetch-Site': 'none', 'Sec-Fetch-User': '?1', 'Upgrade-Insecure-Requests': '1', 'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36', 'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"', 'sec-ch-ua-arch': '""', 'sec-ch-ua-full-version': '"137.0.7151.120"', 'sec-ch-ua-full-version-list': '"Google Chrome";v="137.0.7151.120", "Chromium";v="137.0.7151.120", "Not/A)Brand";v="24.0.0.0"', 'sec-ch-ua-mobile': '?1', 'sec-ch-ua-model': '"Nexus 5"', 'sec-ch-ua-platform': '"Android"', 'sec-ch-ua-platform-version': '"6.0"'}

expected_text = 'boult'
max_workers = 40

print(f"Sending request with {max_workers} concurrent workers...")

session = requests.Session()

def make_single_request():
    try:
        response = session.get(url, headers=headers)
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

        print(f"Response received in {elapsed:.2f} seconds")

    except Exception as e:
        print("⚠️ Request failed:", str(e))
    finally:
        if hasattr(session, 'close'):
            session.close()
