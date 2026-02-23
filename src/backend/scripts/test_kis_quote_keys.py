import requests
import json
import os
import sys
import io

# Force unbuffered stdout
sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8', line_buffering=True)

def test_quote_keys_simple():
    print("STARTING SCRIPT (ROBUST .ENV READ)...", flush=True)
    try:
        # Try multiple locations for .env
        env_locations = [
            os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '.env')),
            os.path.abspath(os.path.join(os.getcwd(), '.env')),
            os.path.abspath(os.path.join(os.getcwd(), 'src', 'backend', '.env')),
            os.path.abspath(r"d:\Workspace\StockThemeBoard\.env")
        ]
        
        env_vars = {}
        env_loaded = False
        
        for env_path in env_locations:
            if os.path.exists(env_path):
                print(f"Index .env at {env_path}", flush=True)
                try:
                    with open(env_path, "r", encoding="utf-8") as f:
                        for line in f:
                            line = line.strip()
                            if not line or line.startswith("#"):
                                continue
                            if "=" in line:
                                key, value = line.split("=", 1)
                                value = value.strip().strip("'").strip('"')
                                env_vars[key.strip()] = value
                    env_loaded = True
                    break
                except Exception as e:
                    print(f"Failed to read {env_path}: {e}", flush=True)
        
        if not env_loaded:
             print("FAILED TO FIND .ENV FILE", flush=True)
             return

        base_url = env_vars.get("KIS_BASE_URL", "https://openapi.koreainvestment.com:9443")
        app_key = env_vars.get("KIS_APP_KEY")
        app_secret = env_vars.get("KIS_APP_SECRET")
        
        print(f"Base URL: {base_url}", flush=True)
        print(f"App Key found: {bool(app_key)}", flush=True)
        
        if not app_key or not app_secret:
             print(">>> KEYS MISSING IN .ENV <<<", flush=True)
             return
        
        # Token
        print("Getting token...", flush=True)
        try:
            # Removed timeout to see if that's the issue, or maybe increase it
            token_res = requests.post(
                f"{base_url}/oauth2/tokenP",
                json={
                    "grant_type": "client_credentials",
                    "appkey": app_key,
                    "appsecret": app_secret
                }
            )
            print(f"Token Response Code: {token_res.status_code}", flush=True)
            if token_res.status_code != 200:
                print(f"Token Failed: {token_res.text}", flush=True)
                return
            token = token_res.json()["access_token"]
            print("Token acquired.", flush=True)
        except Exception as e:
            print(f"Token Request Exception: {e}", flush=True)
            return
        
        # Quote
        print("Getting quote...", flush=True)
        code = "005930" # Samsung
        try:
            quote_res = requests.get(
                f"{base_url}/uapi/domestic-stock/v1/quotations/inquire-price",
                headers={
                    "authorization": f"Bearer {token}",
                    "appkey": app_key,
                    "appsecret": app_secret,
                    "tr_id": "FHKST01010100"
                },
                params={
                    "fid_cond_mrkt_div_code": "J",
                    "fid_input_iscd": code
                }
            )
            
            print(f"Quote Status: {quote_res.status_code}", flush=True)
            
            if quote_res.status_code == 200:
                data = quote_res.json().get("output", {})
                print("\n--- JSON OUTPUT START ---", flush=True)
                print(json.dumps(data, indent=2, ensure_ascii=False), flush=True)
                print("--- JSON OUTPUT END ---", flush=True)
            else:
                print(f"Quote Error: {quote_res.text}", flush=True)
        except Exception as e:
            print(f"Quote Request Exception: {e}", flush=True)

    except Exception as e:
        print(f"Global Error: {e}", flush=True)

if __name__ == "__main__":
    test_quote_keys_simple()
