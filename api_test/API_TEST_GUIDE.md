# API 엔드포인트 테스트 가이드

## ✅ API 개발 완료!

다음 API 엔드포인트가 생성되었습니다:

### Theme API
- `GET /api/v1/themes` - 테마 목록 조회
- `GET /api/v1/themes/{id}` - 테마 상세 조회 (종목 포함)
- `POST /api/v1/themes` - 테마 생성

### Stock API
- `GET /api/v1/stocks` - 종목 목록 조회
- `GET /api/v1/stocks/{code}` - 종목 상세 조회
- `POST /api/v1/stocks` - 종목 생성

---

## 🔄 Backend 재시작

먼저 Backend를 재시작하여 새 코드를 적용합니다:

```bash
docker-compose restart backend
```

재시작 후 로그 확인:
```bash
docker-compose logs -f backend
```

정상 시작되면:
```
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

---

## 🧪 Swagger UI에서 API 테스트

### 1. Swagger UI 접속

브라우저에서 다음 URL로 이동:
```
http://localhost:8000/docs
```

이제 2개의 추가 섹션이 보여야 합니다:
- **themes** - Theme 관련 API
- **stocks** - Stock 관련 API

### 2. 테마 생성 테스트

**POST /api/v1/themes** 클릭:

1. "Try it out" 버튼 클릭
2. Request body 입력:
   ```json
   {
     "name": "2차전지",
     "description": "2차전지 및 배터리 관련주"
   }
   ```
3. "Execute" 버튼 클릭

**예상 응답 (201 Created):**
```json
{
  "name": "2차전지",
  "description": "2차전지 및 배터리 관련주",
  "id": "uuid-generated-here",
  "created_at": "2026-02-07T15:00:00.123456Z",
  "updated_at": "2026-02-07T15:00:00.123456Z"
}
```

### 3. 테마 목록 조회

**GET /api/v1/themes** 클릭:

1. "Try it out" 버튼 클릭
2. 파라미터는 기본값 사용 (skip=0, limit=100)
3. "Execute" 버튼 클릭

**예상 응답 (200 OK):**
```json
[
  {
    "name": "2차전지",
    "description": "2차전지 및 배터리 관련주",
    "id": "uuid-here",
    "created_at": "2026-02-07T15:00:00.123456Z",
    "updated_at": "2026-02-07T15:00:00.123456Z"
  }
]
```

### 4. 종목 생성 테스트

**POST /api/v1/stocks** 클릭:

1. "Try it out" 버튼 클릭
2. Request body 입력:
   ```json
   {
     "code": "005930",
     "name": "삼성전자",
     "market": "KOSPI",
     "market_cap": 400000000000000
   }
   ```
3. "Execute" 버튼 클릭

**예상 응답 (201 Created):**
```json
{
  "code": "005930",
  "name": "삼성전자",
  "market": "KOSPI",
  "market_cap": 400000000000000,
  "created_at": "2026-02-07T15:01:00.123456Z"
}
```

### 5. 종목 조회 테스트

**GET /api/v1/stocks/{code}** 클릭:

1. "Try it out" 버튼 클릭
2. **code** 파라미터에 `005930` 입력
3. "Execute" 버튼 클릭

**예상 응답 (200 OK):**
```json
{
  "code": "005930",
  "name": "삼성전자",
  "market": "KOSPI",
  "market_cap": 400000000000000,
  "created_at": "2026-02-07T15:01:00.123456Z"
}
```

### 6. 더 많은 데이터 생성

추가 테마들:
```json
{"name": "반도체", "description": "반도체 관련주"}
{"name": "바이오", "description": "바이오 및 제약 관련주"}
{"name": "AI", "description": "인공지능 관련주"}
```

추가 종목들:
```json
{"code": "000660", "name": "SK하이닉스", "market": "KOSPI", "market_cap": 80000000000000}
{"code": "035720", "name": "카카오", "market": "KOSPI", "market_cap": 30000000000000}
{"code": "035420", "name": "NAVER", "market": "KOSPI", "market_cap": 50000000000000}
```

---

## ❌ 오류 처리 테스트

### 중복 생성 테스트

동일한 이름의 테마를 다시 생성 시도:
```json
{
  "name": "2차전지",
  "description": "중복 테스트"
}
```

**예상 응답 (400 Bad Request):**
```json
{
  "detail": "Theme with name '2차전지' already exists"
}
```

### 존재하지 않는 데이터 조회

**GET /api/v1/stocks/999999** 호출:

**예상 응답 (404 Not Found):**
```json
{
  "detail": "Stock with code 999999 not found"
}
```

---

## 🗄️ PostgreSQL에서 데이터 확인

```bash
docker exec -it stocktheme-postgres psql -U stockuser -d stocktheme
```

PostgreSQL 내부에서:
```sql
-- 테마 확인
SELECT * FROM themes;

-- 종목 확인
SELECT * FROM stocks;

-- 종료
\q
```

---

## ✅ 검증 체크리스트

- [ ] Backend가 에러 없이 재시작됨
- [ ] Swagger UI에 themes, stocks 섹션이 보임
- [ ] POST /api/v1/themes로 테마 생성 성공
- [ ] GET /api/v1/themes로 목록 조회 성공
- [ ] POST /api/v1/stocks로 종목 생성 성공
- [ ] GET /api/v1/stocks/{code}로 종목 조회 성공
- [ ] 중복 데이터 생성 시 400 에러 응답
- [ ] 존재하지 않는 데이터 조회 시 404 에러 응답
- [ ] PostgreSQL에서 데이터 확인됨

모든 항목이 체크되면 API 개발이 완료되었습니다! 🎉

---

## 다음 단계

API가 정상 작동하면 다음을 진행할 수 있습니다:

1. **한국투자증권 API 연동** - 실시간 시세 조회
2. **테마-종목 매핑 관리** - ThemeStock 관계 설정
3. **WebSocket** - 실시간 시세 업데이트
4. **Frontend 개발** - API 연동
