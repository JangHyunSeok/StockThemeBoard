"""
KIS API 직접 테스트 - 최소 파라미터로 테스트
"""
import asyncio
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.kis_client import get_kis_client


async def test():
    print("=" * 80)
    print("KIS API 거래량 순위 직접 테스트 (15:24 정규장 시간)")
    print("=" * 80)
    
    try:
        print("\n1. KIS 클라이언트 초기화...")
        client = await get_kis_client()
        print("   ✅ 성공\n")
        
        print("2. 토큰 발급...")
        token = await client.get_access_token()
        print(f"   ✅ 토큰: {token[:20]}...\n")
        
        print("3. 거래량 순위 조회 (limit=30)...")  
        rankings = await client.get_volume_rank(limit=30, market="J")
        print(f"   ✅ 성공: {len(rankings)}개 조회됨\n")
        
        if rankings:
            print("상위 3개 종목:")
            for i, stock in enumerate(rankings[:3], 1):
                print(f"  {i}. {stock.get('name', 'N/A'):15s} "
                      f"| 거래대금: {stock.get('trading_value', 0):>15,}원")
        
        print("\n" + "=" * 80)
        print("✅ 모든 테스트 통과!")
        print("=" * 80)
        return True
        
    except Exception as e:
        print(f"\n❌ 에러 발생!")
        print(f"   타입: {type(e).__name__}")
        print(f"   메시지: {str(e)}")
        print("\n상세:")
        import traceback
        traceback.print_exc()
        print("=" * 80)
        return False


if __name__ == "__main__":
    result = asyncio.run(test())
    sys.exit(0 if result else 1)
