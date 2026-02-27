import requests
import json

url = "http://localhost:3000/api/v1/indices/current"

try:
    print(f"📡 Calling {url}...")
    response = requests.get(url, timeout=10)
    print(f"HTTP Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Success!")
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        print(f"❌ Error: {response.text}")

except Exception as e:
    print(f"❌ Exception: {type(e).__name__}: {str(e)}")
