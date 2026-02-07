# Docker 환경 실행 가이드

## 실행 단계

### 1. Docker Desktop 시작
Docker Desktop이 실행 중인지 확인하세요. 
- Windows 작업 표시줄에서 Docker 아이콘을 찾아보세요.
- 아이콘이 초록색이면 실행 중입니다.

### 2. 환경변수 설정 확인
`.env` 파일에서 한국투자증권 API 키가 설정되어 있는지 확인하세요:

```bash
KIS_APP_KEY=실제_앱_키
KIS_APP_SECRET=실제_시크릿
KIS_ACCOUNT_NUMBER=실제_계좌번호
```

> [!NOTE]
> API 키를 아직 입력하지 않았다면, 임시로 `your_app_key_here` 그대로 두어도 컨테이너는 시작됩니다. 
> 다만 한투 API 연동 기능은 나중에 실제 키를 입력해야 작동합니다.

### 3. Docker Compose 실행

**방법 1: 명령 프롬프트 사용**

프로젝트 폴더에서 다음 명령을 실행하세요:

```bash
cd d:\Workspace\StockThemeBoard
docker-compose up -d --build
```

**방법 2: PowerShell 사용**

```powershell
cd d:\Workspace\StockThemeBoard
docker-compose up -d --build
```

### 4. 빌드 및 시작 과정

첫 실행 시 다음과 같은 단계가 진행됩니다:

1. **이미지 다운로드** (수 분 소요)
   - PostgreSQL 16
   - Redis 7
   
2. **백엔드 빌드** (1-2분 소요)
   - Python 패키지 설치
   - FastAPI 애플리케이션 준비
   
3. **프론트엔드 빌드** (2-3분 소요)
   - Node.js 의존성 설치
   - Next.js 설정

4. **컨테이너 시작**
   - postgres → redis → backend → frontend 순서로 시작

### 5. 실행 확인

컨테이너가 모두 시작되었는지 확인:

```bash
docker-compose ps
```

다음과 같이 표시되어야 합니다:

```
NAME                      STATUS
stocktheme-postgres       Up
stocktheme-redis          Up
stocktheme-backend        Up
stocktheme-frontend       Up
```

### 6. 로그 확인

각 서비스의 로그를 확인하여 오류가 없는지 체크:

```bash
# 전체 로그
docker-compose logs

# 특정 서비스 로그
docker-compose logs backend
docker-compose logs frontend

# 실시간 로그 보기
docker-compose logs -f
```

### 7. 서비스 접속

브라우저에서 다음 URL로 접속하여 확인:

- **Frontend**: http://localhost:3000
  - Next.js 페이지가 표시되고 Backend API 상태가 표시되어야 함
  
- **Backend Swagger UI**: http://localhost:8000/docs
  - FastAPI Swagger 문서가 표시되어야 함
  
- **Backend Health Check**: http://localhost:8000/health
  - `{"status":"healthy","environment":"development"}` 응답

### 8. 데이터베이스 접속 테스트

**PostgreSQL 접속:**
```bash
docker exec -it stocktheme-postgres psql -U stockuser -d stocktheme
```

접속 후:
```sql
\l              -- 데이터베이스 목록
\dt             -- 테이블 목록 (아직 없음)
\q              -- 종료
```

**Redis 접속:**
```bash
docker exec -it stocktheme-redis redis-cli
```

접속 후:
```
ping            -- PONG 응답 확인
exit            -- 종료
```

## 문제 해결

### 포트 충돌 오류
만약 `port is already allocated` 오류가 발생하면:

```bash
# 사용 중인 포트 확인
netstat -ano | findstr :3000
netstat -ano | findstr :8000
netstat -ano | findstr :5432
netstat -ano | findstr :6379

# 해당 프로세스 종료 또는 docker-compose.yml에서 포트 변경
```

### Backend 빌드 실패
```bash
# 캐시 없이 다시 빌드
docker-compose build --no-cache backend
docker-compose up -d backend
```

### Frontend 의존성 설치 실패
```bash
# Frontend 컨테이너 재빌드
docker-compose build --no-cache frontend
docker-compose up -d frontend
```

### 전체 재시작
```bash
# 모든 컨테이너 중지 및 삭제
docker-compose down

# 볼륨까지 삭제 (주의: 데이터베이스 데이터도 삭제됨)
docker-compose down -v

# 캐시 없이 완전 재빌드
docker-compose build --no-cache
docker-compose up -d
```

## 다음 단계

Docker 환경이 정상적으로 실행되면:

1. ✅ Frontend에서 Backend API 연결 확인
2. ✅ Swagger UI에서 API 문서 확인
3. ⏳ Phase 2: 백엔드 개발 시작
   - 데이터베이스 모델 작성
   - Alembic 마이그레이션 설정
   - 한투 API 클라이언트 구현
