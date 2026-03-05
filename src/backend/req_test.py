import sys
import traceback
from urllib.request import Request, urlopen
from urllib.error import HTTPError

try:
    url = "http://127.0.0.1:8000/api/v1/rankings/volume-rank-by-theme?market=ALL"
    req = Request(url)
    with urlopen(req) as response:
        with open("backend_response.txt", "w", encoding="utf-8") as f:
            f.write(response.read().decode('utf-8'))
except HTTPError as e:
    with open("backend_response.txt", "w", encoding="utf-8") as f:
        f.write(f"HTTPError: {e.code}\n")
        f.write(e.read().decode('utf-8'))
except Exception as e:
    with open("backend_response.txt", "w", encoding="utf-8") as f:
        f.write(traceback.format_exc())
