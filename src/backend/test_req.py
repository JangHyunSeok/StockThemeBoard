import requests
try:
    resp = requests.get("http://localhost:8000/api/v1/rankings/volume-rank-by-theme?market=ALL")
    print(resp.status_code)
    print(resp.text)
except Exception as e:
    print(e)
