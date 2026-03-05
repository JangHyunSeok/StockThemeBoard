import subprocess

try:
    result = subprocess.run(["docker", "logs", "--tail", "100", "stocktheme-backend"], capture_output=True, text=True, check=True)
    print("LOGS:\n", result.stdout)
    if result.stderr:
        print("STDERR:\n", result.stderr)
except Exception as e:
    print("Error:", e)
