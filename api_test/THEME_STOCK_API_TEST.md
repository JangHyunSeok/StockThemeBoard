# 테마-종목 매핑 API 테스트 가이드

## 🎉 새로 추가된 API

테마와 종목의 관계를 관리하는 3개의 새로운 엔드포인트가 추가되었습니다!

### 새 엔드포인트
- `POST /api/v1/themes/{theme_id}/stocks` - 테마에 종목 추가
- `PUT /api/v1/themes/{theme_id}/stocks/{stock_code}` - 종목 가중치 수정
- `DELETE /api/v1/themes/{theme_id}/stocks/{stock_code}` - 테마에서 종목 제거

---

## 📋 완전한 테스트 시나리오

### 1. Swagger UI 접속

브라우저에서:
```
http://localhost:8000/docs
```

이제 **themes** 섹션에 **6개의 엔드포인트**가 보여야 합니다:
- GET /api/v1/themes
- POST /api/v1/themes
- GET /api/v1/themes/{theme_id}
- **POST /api/v1/themes/{theme_id}/stocks** ⭐ NEW
- **PUT /api/v1/themes/{theme_id}/stocks/{stock_code}** ⭐ NEW
- **DELETE /api/v1/themes/{theme_id}/stocks/{stock_code}** ⭐ NEW

---

### 2. 테스트 데이터 준비

#### Step 1: 테마 생성

**POST /api/v1/themes** 실행:
```json
{
  "name": "2차전지",
  "description": "2차전지 및 배터리 관련주"
}
```

**응답에서 `id`를 복사하세요!** (예: `3fa85f64-5717-4562-b3fc-2c963f66afa6`)

#### Step 2: 종목 3개 생성

**POST /api/v1/stocks** 실행:

종목 1 - 삼성SDI:
```json
{
  "code": "006400",
  "name": "삼성SDI",
  "market": "KOSPI",
  "market_cap": 30000000000000
}
```

종목 2 - LG화학:
```json
{
  "code": "051910",
  "name": "LG화학",
  "market": "KOSPI",
  "market_cap": 50000000000000
}
```

종목 3 - 에코프로비엠:
```json
{
  "code": "247540",
  "name": "에코프로비엠",
  "market": "KOSDAQ",
  "market_cap": 15000000000000
}
```

---

### 3. 테마에 종목 추가 테스트

**POST /api/v1/themes/{theme_id}/stocks** 클릭

#### 테스트 1: 삼성SDI 추가 (가중치 9)

1. **theme_id** 파라미터에 위에서 복사한 테마 UUID 입력
2. Request body:
   ```json
   {
     "stock_code": "006400",
     "weight": 9
   }
   ```
3. "Execute" 클릭

**예상 응답 (201 Created):**
```json
{
  "id": "uuid-generated",
  "theme_id": "your-theme-uuid",
  "stock_code": "006400",
  "weight": 9,
  "created_at": "2026-02-07T15:20:00Z"
}
```

#### 테스트 2: LG화학 추가 (가중치 8)

```json
{
  "stock_code": "051910",
  "weight": 8
}
```

#### 테스트 3: 에코프로비엠 추가 (기본 가중치 5)

```json
{
  "stock_code": "247540",
  "weight": 5
}
```

---

### 4. 테마 상세 조회 - 종목 확인

**GET /api/v1/themes/{theme_id}** 실행:

1. **theme_id** 파라미터에 테마 UUID 입력
2. "Execute" 클릭

**예상 응답:**
```json
{
  "name": "2차전지",
  "description": "2차전지 및 배터리 관련주",
  "id": "your-theme-uuid",
  "created_at": "2026-02-07T15:18:00Z",
  "updated_at": "2026-02-07T15:18:00Z",
  "stocks": [
    {
      "code": "006400",
      "name": "삼성SDI",
      "market": "KOSPI",
      "weight": 9
    },
    {
      "code": "051910",
      "name": "LG화학",
      "market": "KOSPI",
      "weight": 8
    },
    {
      "code": "247540",
      "name": "에코프로비엠",
      "market": "KOSDAQ",
      "weight": 5
    }
  ]
}
```

✅ **확인 포인트:** `stocks` 배열에 방금 추가한 3개 종목이 모두 보여야 합니다!

---

### 5. 가중치 수정 테스트

**PUT /api/v1/themes/{theme_id}/stocks/{stock_code}** 클릭

에코프로비엠의 가중치를 5에서 10으로 수정:

1. **theme_id**: 테마 UUID
2. **stock_code**: `247540`
3. Request body:
   ```json
   {
     "weight": 10
   }
   ```
4. "Execute" 클릭

**예상 응답 (200 OK):**
```json
{
  "id": "...",
  "theme_id": "...",
  "stock_code": "247540",
  "weight": 10,
  "created_at": "2026-02-07T15:20:00Z"
}
```

다시 **GET /api/v1/themes/{theme_id}** 실행하면:
- 에코프로비엠의 weight가 **10**으로 변경되어 있어야 합니다!

---

### 6. 종목 제거 테스트

**DELETE /api/v1/themes/{theme_id}/stocks/{stock_code}** 클릭

LG화학을 테마에서 제거:

1. **theme_id**: 테마 UUID
2. **stock_code**: `051910`
3. "Execute" 클릭

**예상 응답 (204 No Content)**
- 응답 body 없음

다시 **GET /api/v1/themes/{theme_id}** 실행하면:
- `stocks` 배열에 **2개 종목만** 남아야 합니다 (삼성SDI, 에코프로비엠)
- LG화학은 사라져 있어야 합니다!

---

## 💾 PostgreSQL에서 확인

```bash
docker exec -it stocktheme-postgres psql -U stockuser -d stocktheme
```

PostgreSQL 내부에서:

```sql
-- theme_stocks 테이블 확인
SELECT * FROM theme_stocks;

-- 테마와 종목을 JOIN하여 확인
SELECT 
    t.name as theme_name,
    s.code,
    s.name as stock_name,
    ts.weight,
    ts.created_at
FROM theme_stocks ts
JOIN themes t ON ts.theme_id = t.id
JOIN stocks s ON ts.stock_code = s.code
ORDER BY ts.weight DESC;
```

**예상 출력:**
```
  theme_name  | code   | stock_name      | weight |      created_at
--------------+--------+-----------------+--------+---------------------
 2차전지      | 247540 | 에코프로비엠    |     10 | 2026-02-07 15:20:00
 2차전지      | 006400 | 삼성SDI         |      9 | 2026-02-07 15:19:00
```

종료:
```sql
\q
```

---

## ❌ 에러 케이스 테스트

### 테스트 1: 중복 추가

이미 추가된 종목을 다시 추가:
```json
{
  "stock_code": "006400",
  "weight": 7
}
```

**예상 응답 (400 Bad Request):**
```json
{
  "detail": "Stock 006400 is already in theme {theme_id}"
}
```

### 테스트 2: 존재하지 않는 종목 추가

```json
{
  "stock_code": "999999",
  "weight": 5
}
```

**예상 응답 (404 Not Found):**
```json
{
  "detail": "Stock with code 999999 not found"
}
```

### 테스트 3: 잘못된 가중치

```json
{
  "stock_code": "006400",
  "weight": 15
}
```

**예상 응답 (422 Unprocessable Entity):**
```
Validation error: weight must be between 1 and 10
```

---

## ✅ 검증 체크리스트

- [ ] Swagger UI에 새 엔드포인트 3개가 보임
- [ ] 테마에 종목 추가 성공 (201 Created)
- [ ] GET /api/v1/themes/{id}에서 추가된 종목 목록 확인
- [ ] 종목 가중치 수정 성공 (200 OK)
- [ ] 테마에서 종목 제거 성공 (204 No Content)
- [ ] 중복 추가 시 400 에러
- [ ] 존재하지 않는 종목 추가 시 404 에러
- [ ] 잘못된 가중치 입력 시 422 에러
- [ ] PostgreSQL에서 theme_stocks 테이블 데이터 확인

---

## 🎯 다음 단계

모든 테스트가 성공하면:

1. **Option 2: 한국투자증권 API 연동** 진행 준비 완료
   - 실시간 시세 조회
   - 종목 정보 자동 업데이트
   - KIS API 클라이언트 구현

2. **데이터베이스 초기 데이터 준비**
   - 주요 테마 등록 (AI, 반도체, 바이오, 2차전지 등)
   - 대표 종목 등록
   - 테마-종목 매핑 설정
