import subprocess
import os

try:
    with open("d:\\Workspace\\StockThemeBoard\\backend_logs.txt", "w", encoding="utf-8") as f:
        subprocess.run(["docker", "logs", "--tail", "200", "stocktheme-backend"], stdout=f, stderr=f, check=False)
    print("Logs written to d:\\Workspace\\StockThemeBoard\\backend_logs.txt")
except Exception as e:
    print(f"Failed to fetch logs: {e}")
