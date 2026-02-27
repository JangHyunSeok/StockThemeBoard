import requests
import json
import os

# KIS 설정 (환경 변수에서 가져오거나 직접 입력)
APP_KEY = "PSSU8Ln2I1MEpGfb5IOh5gs7dcYZIrk7kZCy"
APP_SECRET = "QQRoB+Z7Wmt7bjdWQUUhGAUbnUYAaVPZeds13W6+lEWyb28W7R6602wk2fCjmj4GaClBqPaiNt8OVyK73y5KaBp9jn/KENU9rKPP4ds3eOcv3nAdmAAn2F9RRasS065Ot9APD2qqwTfAK1dffqjAauoLRLnU5w8RAqXLkv9ubFHQt1IEyPk="
BASE_URL = "https://openapi.koreainvestment.com:9443"

def get_token():
    url = f"{BASE_URL}/oauth2/tokenP"
    body = {
        "grant_type": "client_credentials",
        "appkey": APP_KEY,
        "appsecret": APP_SECRET
    }
    res = requests.post(url, json=body)
    return res.json().get("access_token")

def test():
    token = get_token()
    url = f"{BASE_URL}/uapi/domestic-stock/v1/quotations/inquire-index-price"
    
    # 여러 조합 테스트
    tests = [
        {"div": "U", "iscd": "0001", "name": "KOSPI (U)"},
        {"div": "J", "iscd": "0001", "name": "KOSPI (J)"},
        {"div": "U", "iscd": "1001", "name": "KOSDAQ (U)"},
        {"div": "J", "iscd": "1001", "name": "KOSDAQ (J)"}
    ]
    
    for t in tests:
        print(f"\n--- Testing {t['name']} ---")
        headers = {
            "authorization": f"Bearer {token}",
            "appkey": APP_KEY,
            "appsecret": APP_SECRET,
            "tr_id": "FHPST01010000"
        }
        params = {
            "fid_cond_mrkt_div_code": t["div"],
            "fid_input_iscd": t["iscd"]
        }
        res = requests.get(url, headers=headers, params=params)
        data = res.json()
        print(f"Status: {res.status_code}")
        print(f"Response: {data.get('msg1')} (rt_cd: {data.get('rt_cd')})")
        if data.get("rt_cd") == "0":
            print(f"✅ Success! Price: {data.get('output', {}).get('bstp_nmix_prpr')}")

if __name__ == "__main__":
    test()
