# 백엔드 문제 해결 - 단계별 가이드

## 🔧 파일 수정 완료

`config.py` 파일을 완전히 재작성했습니다. 이제 다음 단계를 진행하세요.

## 📝 1단계: 백엔드 컨테이너 재시작

명령 프롬프트에서 다음 명령어를 **순서대로** 실행하세요:

```bash
# 프로젝트 폴더로 이동
cd /d d:\Workspace\StockThemeBoard

# Backend 컨테이너 중지
docker-compose stop backend

# Backend 컨테이너 삭제
docker-compose rm -f backend

# Backend 컨테이너 재빌드 및 시작
docker-compose up -d backend
```

## 🔍 2단계: 로그 확인

재시작 후 로그를 확인하세요:

```bash
docker-compose logs -f backend
```

### ✅ 정상 실행 시 보여야 할 로그:

```
INFO:     Will watch for changes in these directories: ['/app']
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [1] using WatchFiles
INFO:     Started server process [8]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### ❌ 오류가 있다면:

로그의 **마지막 10-20줄**을 확인하고 어떤 오류 메시지가 있는지 알려주세요.

## 🔍 3단계: 자주 발생하는 오류 및 해결

### 오류 A: "ModuleNotFoundError: No module named 'app'"

**해결:**
```bash
# 컨테이너 내부 확인
docker exec -it stocktheme-backend ls -la /app

# app 폴더가 있는지 확인
# 없다면 완전 재빌드
docker-compose build --no-cache backend
docker-compose up -d backend
```

### 오류 B: "pydantic.errors.PydanticSchemaGenerationError"

**해결:** 이미 수정했습니다. 여전히 발생한다면:
```bash
# 캐시 없이 완전 재빌드
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### 오류 C: "Connection refused" (PostgreSQL)

**해결:**
```bash
# PostgreSQL 상태 확인
docker-compose ps postgres

# PostgreSQL이 healthy가 아니라면
docker-compose restart postgres

# 30초 대기 후
docker-compose restart backend
```

### 오류 D: 아무 로그도 안 나옴

**해결:**
```bash
# 컨테이너 상태 확인
docker-compose ps backend

# STATUS를 확인:
# - Exit (1) 또는 Exit (137) → 시작 실패
# - Restarting → 반복적으로 크래시

# 자세한 로그
docker logs stocktheme-backend
```

## 🧪 4단계: 수동 테스트 (선택사항)

Docker 없이 직접 실행해보기:

```bash
# Backend 폴더로 이동
cd src\backend

# Python 가상환경 생성
python -m venv venv

# 가상환경 활성화
venv\Scripts\activate

# 패키지 설치
pip install -r requirements.txt

# 환경변수 복사 (프로젝트 루트에서)
copy ..\..\. env .env

# Backend 실행
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

정상 실행되면:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

브라우저에서 http://localhost:8000/docs 접속 가능!

## 📊 5단계: 결과 확인

다음 명령어로 최종 확인:

```bash
# 1. 컨테이너 상태
docker-compose ps

# 2. Backend 응답 확인 (새 명령 프롬프트)
curl http://localhost:8000/health

# 또는 PowerShell에서:
Invoke-WebRequest -Uri http://localhost:8000/health
```

**예상 응답:**
```json
{"status":"healthy","environment":"development"}
```

## 💡 여전히 안 된다면

다음 정보를 제공해주세요:

1. **docker-compose ps 결과:**
   ```bash
   docker-compose ps
   ```

2. **Backend 로그 (전체):**
   ```bash
   docker-compose logs backend > backend_logs.txt
   type backend_logs.txt
   ```

3. **발생하는 오류 메시지:**
   - 정확한 에러 텍스트
   - 어느 단계에서 발생하는지

이 정보를 알려주시면 정확한 해결책을 드릴 수 있습니다!
