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
    print(f"Token: {token[:10]}...")
    
    # 1. FHKST03010100 + J (기존 URL - 지수 조회)
    print("\n--- Test 1: FHKST03010100 + J ---")
    url = f"{BASE_URL}/uapi/domestic-stock/v1/quotations/inquire-index-price"
    headers = {"authorization": f"Bearer {token}", "appkey": APP_KEY, "appsecret": APP_SECRET, "tr_id": "FHKST03010100"}
    params = {"FID_COND_MRKT_DIV_CODE": "J", "FID_INPUT_ISCD": "0001"}
    res = requests.get(url, headers=headers, params=params)
    print(f"Status: {res.status_code}, rt_cd: {res.json().get('rt_cd')}, msg: {res.json().get('msg1')}")
    if res.json().get('rt_cd') == '0': print("✅ Success!")

    # 2. FHPST01010000 + J (현재가 TR + J)
    print("\n--- Test 2: FHPST01010000 + J ---")
    headers["tr_id"] = "FHPST01010000"
    res = requests.get(url, headers=headers, params=params)
    print(f"Status: {res.status_code}, rt_cd: {res.json().get('rt_cd')}, msg: {res.json().get('msg1')}")
    if res.json().get('rt_cd') == '0': print("✅ Success!")

    # 3. FHKUP03500100 + J (업종 차트 TR - 지수 현재가 포함)
    print("\n--- Test 3: FHKUP03500100 + J ---")
    url_chart = f"{BASE_URL}/uapi/domestic-stock/v1/quotations/inquire-daily-indexchartprice"
    headers["tr_id"] = "FHKUP03500100"
    params_chart = {
        "FID_COND_MRKT_DIV_CODE": "J",
        "FID_INPUT_ISCD": "0001",
        "FID_PERIOD_DIV_CODE": "D",
        "FID_ORG_ADJ_PRC": "0000000000"
    }
    res = requests.get(url_chart, headers=headers, params=params_chart)
    print(f"Status: {res.status_code}, rt_cd: {res.json().get('rt_cd')}, msg: {res.json().get('msg1')}")
    if res.json().get('rt_cd') == '0':
        print("✅ Success!")
        print(f"Price: {res.json().get('output1', {}).get('bstp_nmix_prpr')}")

if __name__ == "__main__":
    test()
