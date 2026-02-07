# Backend API 실행 안됨 - 문제 해결 가이드

## 현재 상황
- ✅ Frontend (http://localhost:3000) 작동 확인
- ❌ Backend API (http://localhost:8000) 접속 안됨

## 🔍 1단계: 백엔드 컨테이너 상태 확인

명령 프롬프트에서 다음 명령어를 실행하세요:

```bash
docker-compose ps
```

**확인할 내용:**
- `stocktheme-backend` 컨테이너의 STATUS가 무엇인지 확인
  - `Up` → 정상 실행 중 (포트 문제 가능성)
  - `Exit` → 실행 실패 (로그 확인 필요)
  - `Restarting` → 반복적으로 재시작 중 (심각한 오류)

## 🔍 2단계: 백엔드 로그 확인

```bash
docker-compose logs backend
```

또는 최근 100줄만 보기:

```bash
docker-compose logs --tail=100 backend
```

### 예상되는 오류 패턴과 해결 방법

#### 오류 1: 환경변수 파싱 오류

**로그 예시:**
```
pydantic_core._pydantic_core.ValidationError
```

**원인:** `.env` 파일의 `ALLOWED_ORIGINS` 값이 List 형식으로 파싱되지 않음

**해결 방법:**

`.env` 파일을 열고 다음과 같이 수정:

```bash
# 기존 (문제 발생 가능)
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000

# 수정 (JSON 배열 형식)
ALLOWED_ORIGINS=["http://localhost:3000","http://localhost:8000"]
```

또는 `src/backend/app/config.py` 파일을 수정:

```python
# ALLOWED_ORIGINS 설정 변경
ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:8000"

# 사용 시 split으로 리스트 변환
@property
def allowed_origins_list(self) -> List[str]:
    return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
```

#### 오류 2: 모듈을 찾을 수 없음

**로그 예시:**
```
ModuleNotFoundError: No module named 'app'
```

**원인:** Python 경로 문제 또는 requirements.txt 설치 실패

**해결 방법:**

```bash
# 백엔드 컨테이너 재빌드
docker-compose build --no-cache backend
docker-compose up -d backend
```

#### 오류 3: 데이터베이스 연결 실패

**로그 예시:**
```
could not connect to server: Connection refused
Is the server running on host "postgres"
```

**원인:** PostgreSQL이 준비되기 전에 Backend가 시작됨

**해결 방법:**

```bash
# PostgreSQL 상태 확인
docker-compose ps postgres

# PostgreSQL 재시작
docker-compose restart postgres

# Backend 재시작
docker-compose restart backend
```

#### 오류 4: 포트 이미 사용 중

**로그 예시:**
```
OSError: [Errno 98] Address already in use
```

**원인:** 포트 8000이 다른 프로세스에서 사용 중

**확인 방법:**
```bash
netstat -ano | findstr :8000
```

**해결 방법:**

**옵션 A: 다른 프로세스 종료**
```bash
# PID 확인 후
taskkill /PID [PID번호] /F
```

**옵션 B: 포트 변경**

`docker-compose.yml` 파일 수정:
```yaml
backend:
  ports:
    - "8001:8000"  # 8001로 변경
```

그 후:
```bash
docker-compose down
docker-compose up -d
```

이제 http://localhost:8001/docs 로 접속

#### 오류 5: pydantic-settings 버전 문제

**로그 예시:**
```
ImportError: cannot import name 'BaseSettings' from 'pydantic'
```

**해결 방법:**

`src/backend/app/config.py` 수정:
```python
# 기존
from pydantic import BaseSettings

# 수정 후
from pydantic_settings import BaseSettings
```

## 🔧 빠른 해결 방법 (일반적)

### 방법 1: Backend만 재시작

```bash
docker-compose restart backend
docker-compose logs -f backend
```

### 방법 2: Backend 완전 재빌드

```bash
docker-compose stop backend
docker-compose rm -f backend
docker-compose build --no-cache backend
docker-compose up -d backend
docker-compose logs -f backend
```

### 방법 3: 전체 재시작

```bash
docker-compose down
docker-compose up -d --build
docker-compose logs -f
```

## 📋 문제 진단 체크리스트

다음 명령어들을 순서대로 실행하고 결과를 확인하세요:

```bash
# 1. 컨테이너 상태
docker-compose ps

# 2. Backend 로그 (전체)
docker-compose logs backend

# 3. PostgreSQL 연결 확인
docker exec -it stocktheme-postgres pg_isready -U stockuser

# 4. Backend 컨테이너 내부 접속
docker exec -it stocktheme-backend /bin/sh

# 컨테이너 내부에서:
ls -la                    # 파일 구조 확인
cat .env                  # 환경변수 확인
python -c "import app"    # 모듈 import 테스트
exit
```

## 🆘 여전히 해결되지 않았다면

다음 정보를 확인해주세요:

1. **컨테이너 상태**
   ```bash
   docker-compose ps
   ```
   출력 결과 전체

2. **Backend 로그**
   ```bash
   docker-compose logs backend
   ```
   마지막 50줄 정도

3. **.env 파일 내용** (API 키 제외)
   ```bash
   type .env
   ```

이 정보를 제공해주시면 더 정확한 해결책을 드릴 수 있습니다!

## 💡 임시 해결책: Backend 수동 실행

Docker가 계속 문제가 된다면 임시로 로컬에서 Backend를 직접 실행할 수 있습니다:

```bash
cd src\backend

# Python 가상환경 생성
python -m venv venv

# 가상환경 활성화 (Windows)
venv\Scripts\activate

# 패키지 설치
pip install -r requirements.txt

# Backend 실행
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

이렇게 하면 Docker 없이도 Backend를 테스트할 수 있습니다.
