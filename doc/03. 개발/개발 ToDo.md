# StockThemeBoard 개발 ToDo 리스트

> **참고 문서**
> - [분석자료.md](file:///d:/Workspace/StockThemeBoard/doc/01.%20분석/분석자료.md)
> - [설계문서.md](file:///d:/Workspace/StockThemeBoard/doc/02.%20설계/설계문서.md)

---

## 📋 Phase 1: 개발 환경 구축 (완료)

### 1.1 프로젝트 초기 설정
- [x] Git 저장소 초기화
- [x] `.gitignore` 파일 생성 (Python, Node.js, 환경변수)
- [x] README.md 작성 (프로젝트 개요, 설치 방법)
- [x] GitHub 원격 저장소 연결

### 1.2 Docker 환경 구축
- [x] Docker Desktop 설치
- [x] `docker-compose.yml` 작성
  - [x] PostgreSQL 서비스 정의
  - [x] Redis 서비스 정의
  - [x] Backend 서비스 정의
  - [x] Frontend 서비스 정의
  - [ ] Nginx 서비스 정의 (선택적)
- [x] `.env.example` 파일 작성
- [x] Docker 네트워크 및 볼륨 설정

### 1.3 로컬 환경 테스트
- [x] `docker-compose up -d` 실행 확인
- [x] PostgreSQL 연결 테스트 (`psql` 또는 DBeaver)
- [x] Redis 연결 테스트 (`redis-cli ping`)
- [x] Backend API 확인 (http://localhost:8000/docs)
- [x] Frontend 확인 (http://localhost:3000)

---

## 🔧 Phase 2: 백엔드 개발 (완료)

### 2.1 FastAPI 프로젝트 기본 구조
- [x] Python 가상환경 생성 (`python -m venv venv`)
- [x] `requirements.txt` 작성 (FastAPI, SQLAlchemy, Redis, APScheduler, Holidays 등)
- [x] 디렉토리 구조 생성 (`app/`, `app/api/`, `app/core/`, `app/models/`, ...)
- [x] `app/main.py` 기본 FastAPI 앱 생성
- [x] `app/config.py` 환경변수 설정 (`Settings` 클래스)

### 2.2 데이터베이스 설정
- [x] SQLAlchemy 비동기 엔진 설정 (`database.py`)
- [x] Alembic 초기화 (`alembic init alembic`)
- [x] ORM 모델 작성
  - [x] `models/theme.py` (Theme 모델)
  - [x] `models/stock.py` (Stock 모델)
  - [x] `models/theme_stock.py` (ThemeStock 모델)
  - [x] `models/daily_ranking.py` (일일 순위 모델 - New)
- [x] 마이그레이션 적용

### 2.3 한국투자증권 API 연동
- [x] 한국투자증권 API 사용 신청 완료
- [x] `services/kis_client.py` 클라이언트 작성
  - [x] `get_access_token()` - OAuth2 토큰 발급 및 Redis 캐싱
  - [x] `get_stock_quote(stock_code)` - 현재가 조회
  - [x] `get_volume_rank()` - 거래량 상위 종목 조회 (New)

### 2.4 Redis 캐싱 구현
- [x] `services/redis_client.py` 작성
- [x] 캐시 키 설계 및 구현
  - [x] `kis:token` - API 토큰 (24시간)
  - [x] `volume_rank_by_theme` - 순위 데이터 (5초 - 실시간성)

### 2.5 REST API 구현
- [x] `api/v1/themes.py` - 테마 API
- [x] `api/v1/stocks.py` - 종목 API (실시간 시세 포함)
- [x] `api/v1/rankings.py` - 거래량 순위 API (실시간 + DB Hybrid)

### 2.6 스케줄러 및 자동화 (New)
- [x] `app/scheduler` 모듈 구현 (`APScheduler`)
- [x] 매일 15:40 데이터 자동 저장 Job 구현
- [x] `holidays` 라이브러리 기반 공휴일/휴일 처리
- [x] `lifespan` 이벤트로 서버 시작 시 스케줄러 가동

---

## 🎨 Phase 3: 프론트엔드 개발 (완료)

### 3.1 Next.js 프로젝트 설정
- [x] Next.js 14+ 프로젝트 생성 (TypeScript, Tailwind, App Router)
- [x] shadcn/ui 기반 컴포넌트 구성
- [x] React Query (TanStack Query) 설정
- [x] Proxy 설정 (`next.config.js`) - 외부 접속(DDNS) 지원

### 3.2 UI 컴포넌트 및 페이지
- [x] 메인 대시보드 (`/`) - 2x2 그리드, 테마별 TOP 4
- [x] 테마 상세 페이지 (`/themes/[id]`)
- [x] 반응형 디자인 (모바일 2열, 데스크톱 3열)
- [x] 상승(Red)/하락(Blue) 색상 구분 및 포맷팅

### 3.3 데이터 연동
- [x] API 클라이언트 (`lib/api.ts`)
- [x] 커스텀 훅 (`useVolumeRankByTheme`)
- [x] 자동 갱신 (Polling 60초/5초)

---

## 🗄️ Phase 4: 데이터베이스 초기화 (완료)

### 4.1 초기 데이터
- [x] `scripts/seed_data.py` 작성
- [x] 6개 주요 테마 및 종목 데이터 시딩 완료

---

## 🔗 Phase 5: 통합 및 배포 (진행 중)

### 5.1 테스트 및 최적화
- [x] Docker Compose 전체 스택 실행 확인
- [x] API 응답 속도 최적화 (병렬 호출, 캐싱)
- [x] 휴일/공휴일 시나리오 테스트 (Hybrid 모드)
- [ ] 부하 테스트 (선택적)

### 5.2 배포 준비
- [x] Docker Multi-stage 빌드 적용
- [x] 환경변수 분리
- [ ] SSL 인증서 적용 (Nginx - 추후 예정)

---

## 📝 추가 및 개선 사항 (New)

### 완료된 개선 사항
- [x] **외부 접속 지원**: Next.js Proxy Rewrite로 CORS 및 네트워크 문제 해결
- [x] **자동 저장**: 스케줄러 도입으로 데이터 누락 방지
- [x] **공휴일 대응**: `holidays` 라이브러리로 완벽한 휴일 처리
- [x] **실시간성 강화**: 캐시 TTL 단축 (60초 -> 5초) 및 병렬 API 호출 최적화

### 향후 계획 (ToDo)
- [ ] WebSocket 도입 (진짜 실시간 - 선택적)
- [ ] 사용자 인증/로그인
- [ ] 차트 시각화
