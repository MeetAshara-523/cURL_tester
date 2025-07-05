import requests
import httpx
import aiohttp
import asyncio
from curl_cffi import requests as curlcffi_requests

class RequestEngine:
    def __init__(self, engine_name):
        self.engine_name = engine_name
        self.session = None
        self._setup_session()
    
    def _setup_session(self):
        if self.engine_name == "requests":
            self.session = requests.Session()
        elif self.engine_name == "httpx":
            self.session = httpx.Client()
        elif self.engine_name == "aiohttp":
            # aiohttp will be handled differently
            self.session = None
        elif self.engine_name == "curlcffi":
            self.session = curlcffi_requests.Session()
    
    def make_request(self, method, url, headers=None, data=None, json_data=None):
        try:
            if self.engine_name == "requests":
                if method == "POST":
                    response = self.session.post(url, headers=headers, data=data, json=json_data)
                else:
                    response = self.session.get(url, headers=headers)
                return response.text, response.status_code
            
            elif self.engine_name == "httpx":
                if method == "POST":
                    response = self.session.post(url, headers=headers, data=data, json=json_data)
                else:
                    response = self.session.get(url, headers=headers)
                return response.text, response.status_code
            
            elif self.engine_name == "aiohttp":
                # Run aiohttp in async context
                return self._run_aiohttp_request(method, url, headers, data, json_data)
            
            elif self.engine_name == "curlcffi":
                if method == "POST":
                    if json_data:
                        response = self.session.post(url, headers=headers, json=json_data)
                    else:
                        response = self.session.post(url, headers=headers, data=data)
                else:
                    response = self.session.get(url, headers=headers)
                return response.text, response.status_code
                
        except Exception as e:
            raise e
    
    def _run_aiohttp_request(self, method, url, headers, data, json_data):
        async def async_request():
            async with aiohttp.ClientSession() as session:
                if method == "POST":
                    if json_data:
                        async with session.post(url, headers=headers, json=json_data) as response:
                            text = await response.text()
                            return text, response.status
                    else:
                        async with session.post(url, headers=headers, data=data) as response:
                            text = await response.text()
                            return text, response.status
                else:
                    async with session.get(url, headers=headers) as response:
                        text = await response.text()
                        return text, response.status
        
        # Run in new event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(async_request())
        finally:
            loop.close()
    
    def close(self):
        if self.session and hasattr(self.session, 'close'):
            self.session.close()

def get_engine_import_code(engine_name):
    """Returns the import statement for snippet generation"""
    if engine_name == "requests":
        return "import requests"
    elif engine_name == "httpx":
        return "import httpx"
    elif engine_name == "aiohttp":
        return "import aiohttp\nimport asyncio"
    elif engine_name == "curlcffi":
        return "from curl_cffi import requests"
    
def get_engine_session_code(engine_name):
    """Returns session creation code for snippet generation"""
    if engine_name == "requests":
        return "session = requests.Session()"
    elif engine_name == "httpx":
        return "client = httpx.Client()"
    elif engine_name == "aiohttp":
        return "# aiohttp uses async context manager"
    elif engine_name == "curlcffi":
        return "session = requests.Session()"

def get_engine_request_code(engine_name, method, has_data=False):
    """Returns request execution code for snippet generation"""
    if engine_name == "requests":
        if method == "POST":
            return f"response = session.{method.lower()}(url, headers=headers{', data=data' if has_data else ''})"
        else:
            return f"response = session.{method.lower()}(url, headers=headers)"
    
    elif engine_name == "httpx":
        if method == "POST":
            return f"response = client.{method.lower()}(url, headers=headers{', data=data' if has_data else ''})"
        else:
            return f"response = client.{method.lower()}(url, headers=headers)"
    
    elif engine_name == "aiohttp":
        if method == "POST":
            return f"""async with aiohttp.ClientSession() as session:
    async with session.{method.lower()}(url, headers=headers{', data=data' if has_data else ''}) as response:
        text = await response.text()
        status = response.status"""
        else:
            return f"""async with aiohttp.ClientSession() as session:
    async with session.{method.lower()}(url, headers=headers) as response:
        text = await response.text()
        status = response.status"""
    
    elif engine_name == "curlcffi":
        if method == "POST":
            return f"response = session.{method.lower()}(url, headers=headers{', data=data' if has_data else ''})"
        else:
            return f"response = session.{method.lower()}(url, headers=headers)"