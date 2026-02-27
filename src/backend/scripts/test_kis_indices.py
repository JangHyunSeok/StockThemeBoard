import asyncio
import sys
import os
import json

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.kis_client import get_kis_client

async def test_indices():
    print("=" * 50)
    print("KIS API 지수 조회 테스트")
    print("=" * 50)
    
    try:
        client = await get_kis_client()
        print("\n✅ KIS 클라이언트 초기화 성공")
        
        # 코스피(0001) 테스트
        print("\n📞 KOSPI(0001) 조회 중...")
        kospi = await client.get_index_quote("0001")
        print(f"✅ KOSPI 결과: {json.dumps(kospi, indent=2, ensure_ascii=False, default=str)}")
        
        # 코스닥(1001) 테스트
        print("\n📞 KOSDAQ(1001) 조회 중...")
        kosdaq = await client.get_index_quote("1001")
        print(f"✅ KOSDAQ 결과: {json.dumps(kosdaq, indent=2, ensure_ascii=False, default=str)}")
        
        print("\n" + "=" * 50)
        print("모든 테스트 완료")
        print("=" * 50)
        
        return True
        
    except Exception as e:
        print(f"\n❌ 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(test_indices())
    sys.exit(0 if result else 1)
