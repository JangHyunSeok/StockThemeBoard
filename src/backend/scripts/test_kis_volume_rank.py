"""
KIS API 거래량 순위 테스트 스크립트
"""
import asyncio
import sys
sys.path.insert(0, '/app')

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
        
        for stock in rankings[:5]:  # 상위 5개만 출력
            print(f"{stock['rank']}위: {stock['name']} ({stock['code']})")
            print(f"  현재가: {stock['current_price']:,}원")
            print(f"  등락률: {stock['change_rate']:+.2f}%")
            print(f"  거래량: {stock['volume']:,}")
            print(f"  거래대금: {stock['trading_value']:,}원")
            print()
        
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
