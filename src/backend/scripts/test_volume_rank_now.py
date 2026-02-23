"""
거래량 순위 조회 API 평일 저녁 작동 여부 테스트
현재 시각: 21:06 (화요일, 평일)
"""
import sys
from pathlib import Path

# 프로젝트 루트 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import asyncio
from datetime import datetime
from app.services.kis_client import get_kis_client


async def test_volume_rank():
    print("=" * 80)
    print("거래량 순위 조회 API 테스트")
    print("=" * 80)
    print(f"테스트 시각: {datetime.now()}")
    print(f"요일: 화요일 (평일)")
    print(f"KRX 정규장: 종료 (15:30)")
    print(f"시간외거래: 종료 (18:00)")
    print("=" * 80)
    print()
    
    try:
        print("📡 KIS 클라이언트 초기화 중...")
        kis_client = await get_kis_client()
        print("✅ 클라이언트 초기화 완료\n")
        
        # 테스트 1: KRX 거래량 순위 조회
        print("📊 테스트 1: KRX 거래량 순위 조회 (market='J')")
        print("-" * 80)
        try:
            rankings = await kis_client.get_volume_rank(limit=5, market="J")
            
            if rankings:
                print(f"✅ 성공: {len(rankings)}개 종목 조회됨\n")
                print("상위 5개 종목:")
                for i, stock in enumerate(rankings, 1):
                    print(f"  {i}. {stock.get('name', 'N/A'):15s} | "
                          f"종목코드: {stock.get('code', 'N/A'):6s} | "
                          f"거래대금: {stock.get('trading_value', 0):>12,}원")
                print()
                return True
            else:
                print("⚠️  빈 응답 (데이터 없음)\n")
                return False
                
        except Exception as e:
            print(f"❌ KRX 조회 실패")
            print(f"   에러 타입: {type(e).__name__}")
            print(f"   에러 메시지: {str(e)}\n")
            return False
            
    except Exception as e:
        print(f"❌ 클라이언트 초기화 실패")
        print(f"   에러 타입: {type(e).__name__}")
        print(f"   에러 메시지: {str(e)}\n")
        return False


async def main():
    """메인 함수"""
    result = await test_volume_rank()
    
    print("=" * 80)
    if result:
        print("🎉 결론: KIS API가 평일 저녁에도 정상 작동합니다!")
        print("   → 현재 로직 유지 (평일/휴일만 구분)")
    else:
        print("⚠️  결론: KIS API가 평일 저녁에 작동하지 않습니다.")
        print("   → 로직 수정 필요 (시간대 체크 추가)")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
