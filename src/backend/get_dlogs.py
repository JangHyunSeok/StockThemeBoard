import subprocess
try:
    p = subprocess.run(["docker", "logs", "--tail", "50", "stocktheme-backend"], capture_output=True, text=True, check=True)
    with open("d:\\Workspace\\StockThemeBoard\\src\\backend\\dlogs.txt", "w", encoding="utf-8") as f:
        f.write(p.stdout)
        f.write("\n=== STDERR ===\n")
        f.write(p.stderr)
    print("SUCCESS")
except Exception as e:
    print(e)
