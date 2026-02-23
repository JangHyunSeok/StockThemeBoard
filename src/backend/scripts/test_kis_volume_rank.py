"""
KIS API 거래량 순위 테스트 스크립트
"""
import asyncio
import sys
import os
# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.kis_client import get_kis_client


async def test_volume_rank():
    print("=" * 50)
    print("KIS API 거래량 순위 조회 테스트")
    print("=" * 50)
    
    try:
        client = await get_kis_client()
        print("\n✅ KIS 클라이언트 초기화 성공")
        
        print("\n📞 거래량 상위 10개 종목 조회 중...")
        rankings = await client.get_volume_rank(limit=10)
        
        print(f"\n✅ 성공! {len(rankings)}개 종목 조회됨")
        print("\n" + "=" * 50)
        print("조회 결과:")
        print("=" * 50)
        
        for stock in rankings[:1]:  # 상위 1개만 출력 (필드 확인용)
             print(f"Update: Raw data inspection")
             # We need to access the raw data which is not returned by get_volume_rank currently as it filters fields.
             # So I will modify get_volume_rank temporarily or just use the client directly here?
             # Actually get_volume_rank returns a filtered dict. 
             # I should modify the script to call client.client.get directly or modify get_volume_rank to return raw data?
             # Better: I will use the client's internal method if possible, or just look at what get_volume_rank returns.
             # Wait, get_volume_rank returns a list of dictionaries with specific keys.
             # I need to see the RAW response from KIS API. 
             pass

        # To see raw response, I'll direct call the API endpoint in this script using the client's token and http client.
        access_token = await client.get_access_token()
        url = "/uapi/domestic-stock/v1/quotations/volume-rank"
        headers = {
            "authorization": f"Bearer {access_token}",
            "appkey": client.app_key,
            "appsecret": client.app_secret,
            "tr_id": "FHPST01710000"
        }
        params = {
            "fid_cond_mrkt_div_code": "J",
            "fid_cond_scr_div_code": "20171",
            "fid_input_iscd": "0000",
            "fid_div_cls_code": "0",
            "fid_input_cnt_1": "1", # Only 1 for inspection
            "fid_rank_sort_cls_code": "0"
        }
        response = await client.client.get(url, headers=headers, params=params)
        print("\n🔍 Raw Response Item (First Item):")
        if response.status_code == 200:
            data = response.json()
            if "output" in data and len(data["output"]) > 0:
                import json
                print(json.dumps(data["output"][0], indent=2, ensure_ascii=False))
            else:
                print("No output found")
        else:
             print(f"Error: {response.text}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 오류 발생: {str(e)}")
        print(f"오류 타입: {type(e).__name__}")
        import traceback
        print("\n상세 오류:")
        traceback.print_exc()
        return False


if __name__ == "__main__":
    result = asyncio.run(test_volume_rank())
    sys.exit(0 if result else 1)
