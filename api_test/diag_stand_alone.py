import requests
import json
import time

# KIS Credentials from .env
APP_KEY = "PSSU8Ln2I1MEpGfb5IOh5gs7dcYZIrk7kZCy"
APP_SECRET = "QQRoB+Z7Wmt7bjdWQUUhGAUbnUYAaVPZeds13W6+lEWyb28W7R6602wk2fCjmj4GaClBqPaiNt8OVyK73y5KaBp9jn/KENU9rKPP4ds3eOcv3nAdmAAn2F9RRasS065Ot9APD2qqwTfAK1dffqjAauoLRLnU5w8RAqXLkv9ubFHQt1IEyPk="
BASE_URL = "https://openapi.koreainvestment.com:9443"

def get_token():
    print(f"📡 Requesting token from {BASE_URL}...")
    url = f"{BASE_URL}/oauth2/tokenP"
    body = {
        "grant_type": "client_credentials",
        "appkey": APP_KEY,
        "appsecret": APP_SECRET
    }
    try:
        res = requests.post(url, json=body, timeout=10)
        res.raise_for_status()
        token = res.json().get("access_token")
        if token:
            print("✅ Token acquired.")
            return token
        else:
            print(f"❌ Token not found in response: {res.text}")
    except Exception as e:
        print(f"❌ Token request failed: {e}")
    return None

def diagnose():
    token = get_token()
    if not token: return

    # Possible TR IDs and combinations
    tests = [
        {"tr_id": "FHKST03010100", "div": "U", "iscd": "0001", "desc": "Domestic Index (KOSPI)"},
        {"tr_id": "FHKST03010100", "div": "U", "iscd": "1001", "desc": "Domestic Index (KOSDAQ)"},
        {"tr_id": "FHPST01010000", "div": "U", "iscd": "0001", "desc": "Standard Price TR (KOSPI & U)"},
        {"tr_id": "FHPST01010000", "div": "J", "iscd": "0001", "desc": "Standard Price TR (KOSPI & J)"},
    ]

    # KIS API endpoint for index current price
    url = f"{BASE_URL}/uapi/domestic-stock/v1/quotations/inquire-index-price"
    
    results = []

    for t in tests:
        print(f"\n🔬 Testing: {t['desc']}")
        headers = {
            "content-type": "application/json; charset=utf-8",
            "authorization": f"Bearer {token}",
            "appkey": APP_KEY,
            "appsecret": APP_SECRET,
            "tr_id": t["tr_id"],
            "custtype": "P"
        }
        params = {
            "fid_cond_mrkt_div_code": t["div"],
            "fid_input_iscd": t["iscd"]
        }
        
        try:
            res = requests.get(url, headers=headers, params=params, timeout=10)
            print(f"   HTTP {res.status_code}")
            data = res.json()
            rt_cd = data.get("rt_cd")
            msg1 = data.get("msg1")
            print(f"   rt_cd: {rt_cd}, msg1: {msg1}")
            
            t_res = {
                "desc": t["desc"],
                "tr_id": t["tr_id"],
                "params": params,
                "status": res.status_code,
                "data": data
            }
            results.append(t_res)
            
            if rt_cd == "0":
                print("   ✅ SUCCESS!")
            else:
                print(f"   ❌ FAILED: {msg1}")
        except Exception as e:
            print(f"   💥 EXCEPTION: {e}")
            results.append({"desc": t["desc"], "error": str(e)})

    with open("diag_final.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\n💾 Results saved to diag_final.json")

if __name__ == "__main__":
    diagnose()
