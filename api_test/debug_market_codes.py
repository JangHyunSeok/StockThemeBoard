import asyncio
import sys
import os

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src/backend')))

from app.services.kis_client import get_kis_client

async def test_codes():
    client = await get_kis_client()
    access_token = await client.get_access_token()
    url = "/uapi/domestic-stock/v1/quotations/inquire-index-price"
    
    test_values = ["U", "J", "0"]
    indices = ["0001", "1001"]
    
    for val in test_values:
        for iscd in indices:
            print(f"\nTesting: FID_COND_MRKT_DIV_CODE='{val}', FID_INPUT_ISCD='{iscd}'")
            headers = {
                "authorization": f"Bearer {access_token}",
                "appkey": client.app_key,
                "appsecret": client.app_secret,
                "tr_id": "FHPST01010000"
            }
            params = {
                "fid_cond_mrkt_div_code": val,
                "fid_input_iscd": iscd
            }
            try:
                response = await client.client.get(url, headers=headers, params=params)
                data = response.json()
                print(f"Status: {response.status_code}")
                if data.get("rt_cd") == "0":
                    print(f"✅ Success! Current Price: {data.get('output', {}).get('bstp_nmix_prpr')}")
                else:
                    print(f"❌ Fail: {data.get('msg1')}")
            except Exception as e:
                print(f"💥 Exception: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_codes())
