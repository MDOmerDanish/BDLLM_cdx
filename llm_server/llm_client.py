import urllib.request
import json


def query_llm(prompt: str) -> str:
    url = "http://localhost:8000/generate"
    headers = {"Content-Type": "application/json"}
    payload = {"prompt": prompt}
    
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode("utf-8"))
            return result.get("response", "").strip()
    except Exception as e:
        print(f"\n[Error] Failed to connect to Custom LLM Node: {e}")
        return ""
