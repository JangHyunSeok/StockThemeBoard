import urllib.request
import json
import traceback

with open("d:\\Workspace\\StockThemeBoard\\src\\backend\\err.txt", "w") as f:
    try:
        req = urllib.request.Request("http://localhost:8000/api/v1/rankings/volume-rank-by-theme?market=ALL")
        with urllib.request.urlopen(req) as response:
            f.write(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        f.write(f"HTTPError: {e.code}\n")
        f.write(e.read().decode('utf-8'))
    except Exception as e:
        f.write("Other Error:\n")
        f.write(traceback.format_exc())
