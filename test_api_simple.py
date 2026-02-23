"""
간단한 HTTP 테스트 - 백엔드 API 직접 호출
현재 시각: 21:07 (화요일, 평일)
"""
import requests
from datetime import datetime

print("=" * 80)
print("거래량 순위 조회 API 테스트 (HTTP)")
print("=" * 80)
print(f"테스트 시각: {datetime.now()}")
print(f"요일: 화요일 (평일)")
print("=" * 80)
print()

try:
    print("📡 백엔드 API 호출 중...")
    print("URL: http://localhost:3000/api/v1/rankings/volume-rank-by-theme?market=KRX")
    print()
    
    response = requests.get(
        "http://localhost:3000/api/v1/rankings/volume-rank-by-theme?market=KRX",
        timeout=30
    )
    
    print(f"HTTP 상태 코드: {response.status_code}")
    print()
    
    if response.status_code == 200:
        data = response.json()
        print("✅ 성공!")
        print(f"테마 수: {len(data)}")
        
        if data:
            first_theme = list(data.keys())[0]
            stocks = data[first_theme]
            print(f"\n첫 번째 테마: {first_theme}")
            print(f"종목 수: {len(stocks)}")
            
            if stocks:
                print(f"\n상위 3개 종목:")
                for i, stock in enumerate(stocks[:3], 1):
                    print(f"  {i}. {stock.get('name', 'N/A'):15s} | "
                          f"거래대금: {stock.get('trading_value', 0):>12,}원")
        
        print("\n" + "=" * 80)
        print("🎉 결론: 거래량 순위 조회 API가 평일 저녁에도 정상 작동!")
        print("   → 원래 로직 유지 (평일/휴일만 구분)")
        print("=" * 80)
        
    elif response.status_code == 503:
        print("❌ 503 Service Unavailable")
        print(f"에러 메시지: {response.text}")
        print()
        print("=" * 80)
        print("⚠️  결론: API가 평일 저녁에 작동하지 않음")
        print("   → 로직 수정 필요 (시간대 체크 추가)")
        print("=" * 80)
        
    else:
        print(f"⚠️  예상치 못한 응답: {response.status_code}")
        print(f"응답 내용: {response.text[:500]}")
        
except requests.exceptions.ConnectionError:
    print("❌ 연결 실패: 백엔드 서버가 실행 중이 아닙니다")
    print("   docker-compose up -d 로 서버를 시작해주세요")
    
except requests.exceptions.Timeout:
    print("❌ 타임아웃: 서버 응답이 30초 이상 걸립니다")
    
except Exception as e:
    print(f"❌ 에러 발생: {type(e).__name__}: {str(e)}")
