import requests
import json
import os
import sys

def get_quote_keys_file():
    print("Starting file dump script...", flush=True)
    try:
        # Load env vars manually
        env_vars = {}
        # Try standard locations
        possible_env_paths = [
            "/app/.env",
            os.path.join(os.path.dirname(__file__), '../../.env'),
            ".env"
        ]
        
        for path in possible_env_paths:
            if os.path.exists(path):
                print(f"Loading .env from {path}")
                with open(path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith("#"): continue
                        if "=" in line:
                            k, v = line.split("=", 1)
                            env_vars[k.strip()] = v.strip().strip("'").strip('"')
                break
        
        # Fallback to os.environ
        base_url = env_vars.get("KIS_BASE_URL", os.environ.get("KIS_BASE_URL", "https://openapi.koreainvestment.com:9443"))
        app_key = env_vars.get("KIS_APP_KEY", os.environ.get("KIS_APP_KEY"))
        app_secret = env_vars.get("KIS_APP_SECRET", os.environ.get("KIS_APP_SECRET"))
        
        if not app_key:
            print("No APP KEY found!")
            return

        # Get Token
        print("Getting token...")
        token_res = requests.post(
            f"{base_url}/oauth2/tokenP",
            json={
                "grant_type": "client_credentials",
                "appkey": app_key,
                "appsecret": app_secret
            }
        )
        if token_res.status_code != 200:
            print(f"Token failed: {token_res.text}")
            return
            
        token = token_res.json()["access_token"]
        
        # Get Quote
        print("Getting quote...")
        code = "005930" # Samsung
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
        
        print(f"Quote status: {quote_res.status_code}")
        
        output_data = {}
        if quote_res.status_code == 200:
            output_data = quote_res.json().get("output", {})
        else:
            output_data = {"error": quote_res.text}
            
        # Write to file
        with open("/app/quote_response.json", "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
            
        print("Done. Wrote to /app/quote_response.json")
        
    except Exception as e:
        print(f"Error: {e}")
        with open("/app/quote_response.json", "w", encoding="utf-8") as f:
            f.write(str(e))

if __name__ == "__main__":
    get_quote_keys_file()
