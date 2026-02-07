# Docker 서비스 검증 가이드

Docker Compose가 성공적으로 실행되었습니다! 이제 모든 서비스가 정상적으로 작동하는지 확인해보겠습니다.

## 🔍 1단계: 컨테이너 상태 확인

명령 프롬프트에서 다음 명령어를 실행하세요:

```bash
docker-compose ps
```

**예상 출력:**
```
NAME                      COMMAND                  SERVICE      STATUS        PORTS
stocktheme-backend        "uvicorn app.main:ap…"   backend      Up            0.0.0.0:8000->8000/tcp
stocktheme-frontend       "docker-entrypoint.s…"   frontend     Up            0.0.0.0:3000->3000/tcp
stocktheme-postgres       "docker-entrypoint.s…"   postgres     Up (healthy)  0.0.0.0:5432->5432/tcp
stocktheme-redis          "docker-entrypoint.s…"   redis        Up (healthy)  0.0.0.0:6379->6379/tcp
```

> [!IMPORTANT]
> 모든 서비스의 STATUS가 `Up` 또는 `Up (healthy)`여야 합니다.

만약 어떤 서비스가 `Exit` 상태라면 로그를 확인하세요:
```bash
docker-compose logs [서비스명]
# 예: docker-compose logs backend
```

## 🌐 2단계: 브라우저에서 서비스 확인

### ✅ Frontend 확인 (Next.js)

1. 브라우저를 열고 다음 URL로 접속:
   ```
   http://localhost:3000
   ```

2. **예상 결과:**
   - "📊 StockThemeBoard" 제목이 표시됨
   - "🔌 Backend API 상태" 섹션이 있음
   - Backend API 상태가 "✅ 연결됨"으로 표시됨
   - 환경: "development", 상태: "healthy" 표시

3. **만약 페이지가 로딩되지 않는다면:**
   - 몇 분 기다려보세요 (첫 실행 시 npm install 시간 필요)
   - 로그 확인: `docker-compose logs -f frontend`

### ✅ Backend API 문서 확인 (Swagger UI)

1. 브라우저를 열고 다음 URL로 접속:
   ```
   http://localhost:8000/docs
   ```

2. **예상 결과:**
   - FastAPI Swagger UI 페이지가 표시됨
   - "StockThemeBoard API" 제목
   - 2개의 엔드포인트가 보임:
     - `GET /` - 루트 엔드포인트
     - `GET /health` - 헬스체크

3. **Swagger UI에서 API 테스트:**
   - `GET /health` 클릭
   - "Try it out" 버튼 클릭
   - "Execute" 버튼 클릭
   - **Response body:**
     ```json
     {
       "status": "healthy",
       "environment": "development"
     }
     ```

### ✅ Backend Health Check (직접 확인)

1. 브라우저를 열고 다음 URL로 접속:
   ```
   http://localhost:8000/health
   ```

2. **예상 결과:**
   ```json
   {
     "status": "healthy",
     "environment": "development"
   }
   ```

## 🗄️ 3단계: 데이터베이스 연결 확인

### PostgreSQL 테스트

```bash
docker exec -it stocktheme-postgres psql -U stockuser -d stocktheme
```

**psql 접속 후:**
```sql
-- 데이터베이스 목록 확인
\l

-- 현재 연결 정보
\conninfo

-- 종료
\q
```

**예상 출력:**
```
You are connected to database "stocktheme" as user "stockuser"
```

### Redis 테스트

```bash
docker exec -it stocktheme-redis redis-cli ping
```

**예상 출력:**
```
PONG
```

Redis CLI 접속:
```bash
docker exec -it stocktheme-redis redis-cli

# Redis CLI 내부에서:
127.0.0.1:6379> ping
PONG
127.0.0.1:6379> keys *
(empty array)
127.0.0.1:6379> exit
```

## 📊 4단계: 로그 확인

### 전체 로그 보기
```bash
docker-compose logs
```

### 특정 서비스 로그 (최근 50줄)
```bash
docker-compose logs --tail=50 backend
docker-compose logs --tail=50 frontend
docker-compose logs --tail=50 postgres
docker-compose logs --tail=50 redis
```

### 실시간 로그 모니터링
```bash
docker-compose logs -f backend
```
(Ctrl+C로 종료)

## ✅ 검증 체크리스트

모든 항목을 확인하세요:

- [ ] `docker-compose ps`에서 4개 서비스 모두 `Up` 상태
- [ ] http://localhost:3000 접속 성공 (Frontend)
- [ ] Frontend에서 Backend API 연결 상태 "✅ 연결됨" 표시
- [ ] http://localhost:8000/docs 접속 성공 (Swagger UI)
- [ ] Swagger UI에서 `/health` API 테스트 성공
- [ ] PostgreSQL 접속 성공
- [ ] Redis ping 테스트 성공 (PONG 응답)
- [ ] Backend 로그에 에러 없음
- [ ] Frontend 로그에 에러 없음

## ❗ 문제 해결

### Frontend가 로딩되지 않음

**증상:** http://localhost:3000 에서 "This site can't be reached" 또는 무한 로딩

**해결:**
```bash
# Frontend 로그 확인
docker-compose logs frontend

# npm install이 완료되었는지 확인
# 첫 실행 시 2-3분 소요됨
```

**일반적인 원인:**
- npm 의존성 설치 중 (기다려야 함)
- Node.js 패키지 설치 오류

**재시작:**
```bash
docker-compose restart frontend
docker-compose logs -f frontend
```

### Backend API가 응답하지 않음

**증상:** http://localhost:8000 에서 연결 거부

**해결:**
```bash
# Backend 로그 확인
docker-compose logs backend

# Python 패키지 설치 확인
# uvicorn이 시작되었는지 확인
```

**재시작:**
```bash
docker-compose restart backend
docker-compose logs -f backend
```

### 데이터베이스 연결 오류

Backend 로그에 "could not connect to server" 오류가 있다면:

```bash
# PostgreSQL 상태 확인
docker-compose ps postgres

# PostgreSQL 재시작
docker-compose restart postgres

# Backend 재시작
docker-compose restart backend
```

### 포트 충돌

"port is already allocated" 오류:

```bash
# 포트 사용 확인
netstat -ano | findstr :3000
netstat -ano | findstr :8000

# 충돌하는 프로세스 종료 또는
# docker-compose.yml에서 포트 변경
```

## 🎉 성공!

모든 검증 항목이 체크되었다면 Docker 환경 구축이 완료되었습니다!

### 다음 단계

이제 Phase 2: 백엔드 개발을 시작할 수 있습니다:

1. **데이터베이스 모델링**
   - SQLAlchemy ORM 모델 작성
   - Alembic 마이그레이션 설정

2. **한투 API 클라이언트**
   - OAuth2 토큰 발급
   - 실시간 시세 조회

3. **REST API 구현**
   - 테마 API 엔드포인트
   - 종목 API 엔드포인트

## 📝 서비스 관리 명령어

```bash
# 전체 서비스 시작
docker-compose up -d

# 전체 서비스 중지
docker-compose down

# 특정 서비스 재시작
docker-compose restart [서비스명]

# 로그 보기
docker-compose logs -f [서비스명]

# 컨테이너 상태 확인
docker-compose ps

# 컨테이너 내부 접속
docker exec -it [컨테이너명] /bin/sh
# 예: docker exec -it stocktheme-backend /bin/sh
```
