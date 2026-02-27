import asyncio
import sys
import os
import json
import httpx

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src/backend')))

from app.services.kis_client import get_kis_client

async def diagnose():
    results = []
    results.append("=" * 80)
    results.append("KIS API 지수 조회를 위한 정밀 진단 시작")
    results.append("=" * 80)
    
    try:
        client = await get_kis_client()
        token = await client.get_access_token()
        results.append(f"✅ Access Token 획득 성공")

        combinations = [
            {"tr_id": "FHKST03010100", "div": "U", "iscd": "0001", "desc": "국내업종 현재지수 (KOSPI)"},
            {"tr_id": "FHKST03010100", "div": "U", "iscd": "1001", "desc": "국내업종 현재지수 (KOSDAQ)"},
            {"tr_id": "FHPST01010000", "div": "U", "iscd": "0001", "desc": "전통적 현재가 TR (KOSPI)"},
            {"tr_id": "FHPST01010000", "div": "J", "iscd": "0001", "desc": "전통적 현재가 TR (KOSPI, Div J)"},
        ]

        async with httpx.AsyncClient(base_url=client.base_url, timeout=10.0) as http_client:
            for combo in combinations:
                results.append(f"\n🔍 테스트: {combo['desc']}")
                results.append(f"   TR_ID: {combo['tr_id']}, DIV: {combo['div']}, ISCD: {combo['iscd']}")
                
                headers = {
                    "content-type": "application/json; charset=utf-8",
                    "authorization": f"Bearer {token}",
                    "appkey": client.app_key,
                    "appsecret": client.app_secret,
                    "tr_id": combo['tr_id'],
                    "custtype": "P"
                }
                params = {
                    "fid_cond_mrkt_div_code": combo['div'],
                    "fid_input_iscd": combo['iscd']
                }
                
                try:
                    url = "/uapi/domestic-stock/v1/quotations/inquire-index-price"
                    response = await http_client.get(url, headers=headers, params=params)
                    
                    results.append(f"   HTTP Status: {response.status_code}")
                    if response.status_code == 200:
                        data = response.json()
                        rt_cd = data.get("rt_cd")
                        msg1 = data.get("msg1")
                        results.append(f"   rt_cd: {rt_cd}, msg1: {msg1}")
                        if rt_cd == "0":
                            results.append("   ✅ 성공! 응답 데이터 원본:")
                            results.append(json.dumps(data, indent=2, ensure_ascii=False))
                        else:
                            results.append(f"   ❌ API 오류: {msg1}")
                            results.append(f"   전체 응답: {json.dumps(data, ensure_ascii=False)}")
                    else:
                        results.append(f"   ❌ HTTP 오류: {response.text}")
                except Exception as e:
                    results.append(f"   💥 예외 발생: {str(e)}")

    except Exception as e:
        results.append(f"❌ 진단 중 치명적 오류: {str(e)}")
        import traceback
        results.append(traceback.format_exc())

    with open("diag_results.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(results))

if __name__ == "__main__":
    asyncio.run(diagnose())
