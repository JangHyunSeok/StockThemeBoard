import requests
import json

APP_KEY = "PSSU8Ln2I1MEpGfb5IOh5gs7dcYZIrk7kZCy"
APP_SECRET = "QQRoB+Z7Wmt7bjdWQUUhGAUbnUYAaVPZeds13W6+lEWyb28W7R6602wk2fCjmj4GaClBqPaiNt8OVyK73y5KaBp9jn/KENU9rKPP4ds3eOcv3nAdmAAn2F9RRasS065Ot9APD2qqwTfAK1dffqjAauoLRLnU5w8RAqXLkv9ubFHQt1IEyPk="
BASE_URL = "https://openapi.koreainvestment.com:9443"

def get_token():
    url = f"{BASE_URL}/oauth2/tokenP"
    res = requests.post(url, json={"grant_type": "client_credentials", "appkey": APP_KEY, "appsecret": APP_SECRET})
    return res.json().get("access_token")

def test():
    token = get_token()
    url = f"{BASE_URL}/uapi/domestic-stock/v1/quotations/inquire-index-price"
    headers = {
        "authorization": f"Bearer {token}",
        "appkey": APP_KEY,
        "appsecret": APP_SECRET,
        "tr_id": "FHKST03010100"
    }
    # Test KOSPI
    params = {
        "fid_cond_mrkt_div_code": "U",
        "fid_input_iscd": "0001"
    }
    res = requests.get(url, headers=headers, params=params)
    print(f"KOSPI Result: {res.json().get('msg1')} | rt_cd: {res.json().get('rt_cd')}")
    if res.json().get('rt_cd') == '0':
        print(f"✅ Price: {res.json().get('output', {}).get('bstp_nmix_prpr')}")

if __name__ == "__main__":
    test()
