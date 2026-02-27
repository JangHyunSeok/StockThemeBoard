import asyncio
import sys
import os
import json
import httpx

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src/backend')))

from app.services.kis_client import get_kis_client

async def test_combos():
    print("=" * 80)
    print("지수 조회를 위한 다양한 TR ID 및 시장 코드 조합 테스트")
    print("=" * 80)
    
    try:
        client = await get_kis_client()
        token = await client.get_access_token()
        
        # 테스트할 조합들
        combos = [
            # 1. 기존 URL + J 코드
            {"url": "/uapi/domestic-stock/v1/quotations/inquire-index-price", "tr_id": "FHKST03010100", "div": "J", "iscd": "0001", "name": "FHKST03010100 + J (KOSPI)"},
            # 2. 업종 전용 TR ID (FHKUP03500100) + J 코드
            {"url": "/uapi/domestic-stock/v1/quotations/inquire-daily-indexchartprice", "tr_id": "FHKUP03500100", "div": "J", "iscd": "0001", "name": "FHKUP03500100 + J (KOSPI)"},
            # 3. 업종 전용 TR ID (FHKUP03500100) + U 코드
            {"url": "/uapi/domestic-stock/v1/quotations/inquire-daily-indexchartprice", "tr_id": "FHKUP03500100", "div": "U", "iscd": "0001", "name": "FHKUP03500100 + U (KOSPI)"},
            # 4. 다른 가능성 (통합 코드 UN)
            {"url": "/uapi/domestic-stock/v1/quotations/inquire-index-price", "tr_id": "FHKST03010100", "div": "UN", "iscd": "0001", "name": "FHKST03010100 + UN (KOSPI)"},
            # 5. FHPST01010000 + J
            {"url": "/uapi/domestic-stock/v1/quotations/inquire-index-price", "tr_id": "FHPST01010000", "div": "J", "iscd": "0001", "name": "FHPST01010000 + J (KOSPI)"}
        ]

        async with httpx.AsyncClient(base_url=client.base_url, timeout=10.0) as http_client:
            for c in combos:
                print(f"\n▶ 테스트: {c['name']}")
                headers = {
                    "content-type": "application/json; charset=utf-8",
                    "authorization": f"Bearer {token}",
                    "appkey": client.app_key,
                    "appsecret": client.app_secret,
                    "tr_id": c["tr_id"],
                    "custtype": "P"
                }
                params = {
                    "fid_cond_mrkt_div_code": c["div"],
                    "fid_input_iscd": c["iscd"]
                }
                # 만약 차트 API라면 추가 파라미터가 필요할 수 있음
                if "indexchartprice" in c["url"]:
                    params.update({
                        "fid_period_div_code": "D",
                        "fid_org_adj_prc": "0000000000"
                    })

                try:
                    response = await http_client.get(c["url"], headers=headers, params=params)
                    data = response.json()
                    print(f"   Status: {response.status_code}")
                    print(f"   rt_cd: {data.get('rt_cd')}, msg1: {data.get('msg1')}")
                    if data.get("rt_cd") == "0":
                        print("   ✅ 성공!")
                        # 응답 필드 확인 (bstp_nmix_prpr 등)
                        output = data.get("output", {})
                        if isinstance(output, list) and len(output) > 0:
                            output = output[0] # 차트 API인 경우 리스트일 수 있음
                        print(f"   현재가 필드 확인: {output.get('bstp_nmix_prpr') or output.get('stck_prpr')}")
                except Exception as e:
                    print(f"   ❌ 오류: {str(e)}")

    except Exception as e:
        print(f"💥 치명적 오류: {e}")

if __name__ == "__main__":
    asyncio.run(test_combos())
