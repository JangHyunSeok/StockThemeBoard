import urllib.request
import json

try:
    req = urllib.request.Request("http://localhost:8000/api/v1/rankings/volume-rank-by-theme?market=ALL")
    with urllib.request.urlopen(req) as response:
        print(response.read().decode('utf-8'))
except urllib.error.HTTPError as e:
    print("HTTPError:", e.code)
    print(e.read().decode('utf-8'))
except Exception as e:
    print("Other Error:", e)
