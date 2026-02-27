import requests
import json

APP_KEY = "PSSU8Ln2I1MEpGfb5IOh5gs7dcYZIrk7kZCy"
APP_SECRET = "QQRoB+Z7Wmt7bjdWQUUhGAUbnUYAaVPZeds13W6+lEWyb28W7R6602wk2fCjmj4GaClBqPaiNt8OVyK73y5KaBp9jn/KENU9rKPP4ds3eOcv3nAdmAAn2F9RRasS065Ot9APD2qqwTfAK1dffqjAauoLRLnU5w8RAqXLkv9ubFHQt1IEyPk="
BASE_URL = "https://openapi.koreainvestment.com:9443"

def get_token():
    url = f"{BASE_URL}/oauth2/tokenP"
    res = requests.post(url, json={"grant_type": "client_credentials", "appkey": APP_KEY, "appsecret": APP_SECRET})
    return res.json().get("access_token")

def test_combination(token, tr_id, div_code, iscd):
    url = f"{BASE_URL}/uapi/domestic-stock/v1/quotations/inquire-index-price"
    headers = {
        "authorization": f"Bearer {token}",
        "appkey": APP_KEY,
        "appsecret": APP_SECRET,
        "tr_id": tr_id
    }
    params = {
        "fid_cond_mrkt_div_code": div_code,
        "fid_input_iscd": iscd
    }
    try:
        res = requests.get(url, headers=headers, params=params)
        data = res.json()
        print(f"TR_ID: {tr_id} | DIV: {div_code} | ISCD: {iscd} | Status: {res.status_code}")
        print(f"Result: {data.get('msg1')} (rt_cd: {data.get('rt_cd')})")
        if data.get("rt_cd") == "0":
            print("✅ SUCCESS!")
            print(json.dumps(data.get('output', {}), indent=2, ensure_ascii=False))
            return True
    except Exception as e:
        print(f"Error: {e}")
    return False

def run():
    token = get_token()
    print("Starting tests...\n")
    
    # Try combinations
    tr_ids = ["FHPST01010000", "FHKST03010100"]
    div_codes = ["U", "J", "0001", "1001", "0", "1"]
    index_codes = ["0001", "1001"]
    
    for tr in tr_ids:
        for div in div_codes:
            for iscd in index_codes:
                if test_combination(token, tr, div, iscd):
                    print("\n🎉 FOUND WORKING COMBINATION!")
                    # Stop if we find a working one for KOSPI
                    if iscd == "0001": break

if __name__ == "__main__":
    run()
