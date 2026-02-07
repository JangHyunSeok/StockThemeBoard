# Seed Data 스크립트

초기 데이터를 데이터베이스에 추가하는 스크립트입니다.

## 생성되는 데이터

### 📋 테마 (6개)
1. **인공지능(AI)** - AI 반도체, 데이터센터, 생성형 AI
2. **반도체** - 메모리, 시스템 반도체, 장비
3. **2차전지** - 배터리 및 소재
4. **바이오/헬스케어** - 제약, 바이오 신약, 의료기기
5. **전기차** - 전기차, 자율주행, 모빌리티
6. **2차전지 소재** - 양극재, 음극재, 전해액, 분리막

### 📈 종목 (12개)
- 삼성전자, SK하이닉스 (반도체/AI)
- LG에너지솔루션, 에코프로비엠, 에코프로 (2차전지)
- LG화학, SK이노베이션 (화학/소재)
- 현대차, 기아 (전기차)
- 삼성바이오로직스, 셀트리온, SK바이오팜 (바이오)

### 🔗 테마-종목 매핑 (19개)
각 테마에 관련 종목을 가중치(1-10)와 함께 매핑

## 실행 방법

### Backend 컨테이너 내부에서 실행

```bash
# 컨테이너 접속
docker exec -it stocktheme-backend /bin/sh

# 스크립트 실행
cd /app
python scripts/seed_data.py

# 종료
exit
```

## 예상 출력

```
🌱 데이터베이스 초기화 시작...

📋 테마 생성 중...
  ✅ 인공지능(AI)
  ✅ 반도체
  ✅ 2차전지
  ✅ 바이오/헬스케어
  ✅ 전기차
  ✅ 2차전지 소재

총 6개 테마 생성 완료!

📈 종목 등록 중...
  ✅ 삼성전자 (005930)
  ✅ SK하이닉스 (000660)
  ...

총 12개 종목 등록 완료!

🔗 테마-종목 매핑 중...
  ✅ 인공지능(AI) ← 삼성전자 (가중치: 10)
  ✅ 인공지능(AI) ← SK하이닉스 (가중치: 9)
  ...

총 19개 매핑 완료!

============================================================
🎉 초기 데이터 생성 완료!
============================================================

📊 생성된 데이터:
  - 테마: 6개
  - 종목: 12개
  - 매핑: 19개

✨ 이제 API를 통해 데이터를 조회할 수 있습니다!
   👉 http://localhost:8000/docs
```

## 데이터 확인

### Swagger UI에서 확인
```
http://localhost:8000/docs

# 테마 목록 조회
GET /api/v1/themes

# 테마 상세 (종목 포함)
GET /api/v1/themes/{theme_id}

# 종목 목록 조회
GET /api/v1/stocks
```

### PostgreSQL에서 확인
```bash
docker exec -it stocktheme-postgres psql -U stockuser -d stocktheme

# 테마 확인
SELECT * FROM themes;

# 종목 확인
SELECT * FROM stocks;

# 매핑 확인
SELECT 
    t.name as theme_name,
    s.name as stock_name,
    ts.weight
FROM theme_stocks ts
JOIN themes t ON ts.theme_id = t.id
JOIN stocks s ON ts.stock_code = s.code
ORDER BY t.name, ts.weight DESC;
```

## 주의사항

- 중복 실행 시 에러 발생 (이미 데이터 존재)
- 데이터 초기화가 필요하면 DB를 먼저 비워야 함
- 시가총액은 임의 값 (실제와 다를 수 있음)
