# StockThemeBoard 개발 ToDo 리스트

> **참고 문서**
> - [분석자료.md](file:///d:/Workspace/StockThemeBoard/doc/01.%20분석/분석자료.md)
> - [설계문서.md](file:///d:/Workspace/StockThemeBoard/doc/02.%20설계/설계문서.md)

---

## 📋 Phase 1: 개발 환경 구축

### 1.1 프로젝트 초기 설정
- [x] Git 저장소 초기화
  ```bash
  git init
  git add .
  git commit -m "Initial commit"
  ```
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

## 🔧 Phase 2: 백엔드 개발

### 2.1 FastAPI 프로젝트 기본 구조
- [x] Python 가상환경 생성 (`python -m venv venv`)
- [x] `requirements.txt` 작성
  - [x] fastapi
  - [x] uvicorn[standard]
  - [x] sqlalchemy[asyncio]
  - [x] asyncpg
  - [x] redis
  - [x] pydantic-settings
  - [x] python-dotenv
  - [x] requests
  - [x] websockets
- [x] 디렉토리 구조 생성 (`app/`, `app/api/`, `app/core/`, `app/models/`, ...)
- [x] `app/main.py` 기본 FastAPI 앱 생성
- [x] `app/config.py` 환경변수 설정 (`Settings` 클래스)

> **참고**: 현재 버전은 공개 접근 앱으로 사용자 인증 기능이 없습니다.

### 2.2 데이터베이스 설정
- [ ] SQLAlchemy 비동기 엔진 설정 (`database.py`)
- [ ] Alembic 초기화 (`alembic init alembic`)
- [ ] ORM 모델 작성
  - [ ] `models/theme.py` (Theme 모델)
  - [ ] `models/stock.py` (Stock 모델)
  - [ ] `models/theme_stock.py` (ThemeStock 모델)
- [ ] 첫 번째 마이그레이션 생성
  ```bash
  alembic revision --autogenerate -m "Create initial tables"
  alembic upgrade head
  ```

### 2.3 한국투자증권 API 연동
- [x] 한국투자증권 API 사용 신청 완료
- [ ] `core/kis_api.py` 클라이언트 작성
  - [ ] `get_access_token()` - OAuth2 토큰 발급
  - [ ] `get_stock_price(stock_code)` - 현재가 조회
  - [ ] `subscribe_realtime_price()` - WebSocket 실시간 구독
- [ ] 토큰 발급 테스트 (한투 계좌 필요)
- [ ] 실제 종목 시세 조회 테스트 (예: 삼성전자 005930)

### 2.4 Redis 캐싱 구현
- [ ] `core/redis_client.py` 작성
- [ ] 캐시 키 설계 구현
  - [ ] `stock:price:{stock_code}` - 주가 캐싱
  - [ ] `theme:volume:top5:{theme_id}` - 거래량 TOP 5
  - [ ] `theme:trading_value:top5:{theme_id}` - 거래대금 TOP 5
  - [ ] `kis:access_token` - API 토큰 저장
- [ ] TTL 설정 (주가: 10초, 순위: 30초, 토큰: 24시간)

### 2.5 REST API 구현
- [ ] `api/v1/themes.py` - 테마 API
  - [ ] `GET /api/v1/themes` - 테마 목록 조회
  - [ ] `GET /api/v1/themes/{theme_id}` - 테마 상세
  - [ ] `GET /api/v1/themes/{theme_id}/top5` - TOP 5 조회
  - [ ] `POST /api/v1/themes` - 테마 생성 (관리자용)
- [ ] `api/v1/stocks.py` - 종목 API
  - [ ] `GET /api/v1/stocks/{stock_code}` - 종목 상세
  - [ ] `GET /api/v1/stocks/search` - 종목 검색
- [ ] Pydantic 스키마 작성 (`schemas/`)

### 2.6 WebSocket 구현
- [ ] `core/websocket_manager.py` - 연결 관리자
  - [ ] `connect()` / `disconnect()` - 클라이언트 연결 관리
  - [ ] `subscribe_theme()` - 테마 구독
  - [ ] `broadcast_theme_update()` - 브로드캐스트
- [ ] `api/v1/websocket.py` - WebSocket 엔드포인트
- [ ] 실시간 시세 수신 → 캐시 업데이트 → 클라이언트 푸시 플로우

### 2.7 비동기 백그라운드 작업
- [ ] `tasks/update_prices.py` - 30초마다 순위 재계산
- [ ] `tasks/refresh_token.py` - 1시간마다 토큰 갱신 체크
- [ ] `core/ranking_calculator.py` - 순위 계산 로직
  - [ ] `calculate_volume_top5()`
  - [ ] `calculate_trading_value_top5()`

### 2.8 백엔드 테스트
- [ ] Pytest 설정 (`tests/conftest.py`)
- [ ] API 단위 테스트 작성 (`tests/api/`)
- [ ] KIS API 모킹 테스트
- [ ] Swagger UI 확인 (`http://localhost:8000/docs`)

---

## 🎨 Phase 3: 프론트엔드 개발

### 3.1 Next.js 프로젝트 생성
- [ ] Next.js 14+ 프로젝트 생성
  ```bash
  npx create-next-app@latest frontend --typescript --tailwind --app
  ```
- [ ] shadcn/ui 설치
  ```bash
  npx shadcn-ui@latest init
  ```
- [ ] 기본 컴포넌트 설치 (button, card, table, tabs 등)

### 3.2 프로젝트 구조 설정
- [ ] `lib/api.ts` - API 클라이언트 (axios 또는 fetch)
- [ ] `lib/websocket.ts` - WebSocket 클라이언트
- [ ] `types/` - TypeScript 타입 정의
- [ ] `store/` - Zustand 스토어 설정

### 3.3 API 연동
- [ ] API 클라이언트 작성
  - [ ] `fetchThemes()` - 테마 목록 조회
  - [ ] `fetchThemeDetail(id)` - 테마 상세
  - [ ] `fetchThemeTop5(id, sortBy)` - TOP 5 조회
  - [ ] `fetchStockDetail(code)` - 종목 상세
- [ ] 환경변수 설정 (`.env.local`)
  ```
  NEXT_PUBLIC_API_URL=http://localhost:8000
  NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws
  ```

### 3.4 상태 관리 (Zustand)
- [ ] `store/themeStore.ts` - 테마 상태 관리
  - [ ] themes 목록
  - [ ] selectedTheme
  - [ ] favoriteThemeIds (로컬스토리지 연동)
- [ ] `store/stockStore.ts` - 종목 상태 관리
- [ ] `store/websocketStore.ts` - WebSocket 연결 상태

### 3.5 UI 컴포넌트 개발
- [ ] `components/themes/ThemeList.tsx` - 테마 목록
- [ ] `components/themes/ThemeCard.tsx` - 테마 카드
- [ ] `components/themes/ThemeSearch.tsx` - 검색
- [ ] `components/stocks/StockTop5Table.tsx` - TOP 5 테이블
  - [ ] 거래량/거래대금 탭
  - [ ] 실시간 업데이트 표시
- [ ] `components/stocks/StockPriceCard.tsx` - 종목 가격 카드
- [ ] `components/charts/VolumeChart.tsx` - 거래량 차트 (Recharts)
- [ ] `components/charts/TradingValueChart.tsx` - 거래대금 차트

### 3.6 페이지 구현
- [ ] `app/page.tsx` - 메인 대시보드
  - [ ] 즐겨찾기 테마 섹션
  - [ ] 전체 테마 목록
  - [ ] 테마별 TOP 5 표시
- [ ] `app/themes/[id]/page.tsx` - 테마 상세 페이지
- [ ] `app/stocks/[code]/page.tsx` - 종목 상세 페이지 (선택적)

### 3.7 WebSocket 실시간 연동
- [ ] WebSocket 연결 Hook (`useWebSocket`)
- [ ] 테마 구독/구독 취소 기능
- [ ] 실시간 순위 업데이트 UI 반영
- [ ] 연결 상태 표시 (연결됨/끊김)
- [ ] 자동 재연결 로직

### 3.8 스타일링 및 UX
- [ ] Tailwind CSS 커스텀 테마 설정
- [ ] 다크모드 지원 (선택적)
- [ ] 로딩 상태 표시 (Skeleton UI)
- [ ] 에러 처리 (Toast 알림)
- [ ] 반응형 디자인 (모바일 대응)

---

## 🗄️ Phase 4: 데이터베이스 초기화

### 4.1 샘플 테마 데이터 준비
- [ ] 테마 데이터 수집 (네이버 금융, 증권사 리서치 등)
  - [ ] 2차전지 관련 종목
  - [ ] AI 관련 종목
  - [ ] 반도체 관련 종목
  - [ ] 바이오 관련 종목
  - [ ] (5~10개 테마 준비)
- [ ] CSV 또는 JSON 형식으로 정리
  ```json
  {
    "theme_name": "2차전지",
    "stocks": [
      {"code": "373220", "name": "LG에너지솔루션", "weight": 10},
      {"code": "006400", "name": "삼성SDI", "weight": 9}
    ]
  }
  ```

### 4.2 데이터 삽입 스크립트
- [ ] `scripts/seed_data.py` 작성
- [ ] Themes 테이블 삽입
- [ ] Stocks 테이블 삽입
- [ ] ThemeStock 매핑 삽입
- [ ] 스크립트 실행 및 확인

---

## 🔗 Phase 5: 통합 및 테스트

### 5.1 End-to-End 테스트
- [ ] Docker Compose 전체 스택 실행
- [ ] 프론트엔드 → 백엔드 API 호출 테스트
- [ ] WebSocket 실시간 연동 테스트
- [ ] 한투 API 실제 시세 수신 확인
- [ ] Redis 캐싱 동작 확인

### 5.2 성능 테스트
- [ ] 100개 종목 동시 조회 성능 측정
- [ ] API 응답 시간 확인 (목표: 1초 이내)
- [ ] WebSocket 동시 접속 테스트
- [ ] Redis 캐시 히트율 확인

### 5.3 버그 수정 및 개선
- [ ] 에러 로그 확인 및 수정
- [ ] UX 개선사항 반영
- [ ] 코드 리팩토링

---

## 🚀 Phase 6: 배포

### 6.1 프로덕션 빌드
- [ ] 백엔드 Dockerfile 최적화
- [ ] 프론트엔드 프로덕션 빌드 (`npm run build`)
- [ ] 환경변수 프로덕션 설정

### 6.2 서버 배포 (AWS / DigitalOcean / Lightsail)
- [ ] 서버 인스턴스 생성
- [ ] Docker 및 Docker Compose 설치
- [ ] 프로젝트 코드 배포 (Git clone)
- [ ] `.env` 파일 설정 (프로덕션 API 키)
- [ ] `docker-compose up -d` 실행

### 6.3 도메인 및 SSL
- [ ] 도메인 구입 (선택적)
- [ ] Nginx SSL 인증서 설정 (Let's Encrypt)
- [ ] HTTPS 강제 리다이렉트

### 6.4 CI/CD 파이프라인
- [ ] GitHub Actions 워크플로우 작성
- [ ] 자동 테스트 실행
- [ ] 자동 배포 설정

### 6.5 모니터링
- [ ] Sentry 에러 트래킹 설정
- [ ] 로그 수집 (CloudWatch, 파일 로그)
- [ ] 헬스체크 엔드포인트 (`/health`)

---

## 📝 추가 작업 (선택적)

### 사용자 인증 (Phase 3 또는 향후 기능)
> **현재 버전에서는 제외**: 공개 접근 앱으로 개발합니다.
- [ ] JWT 기반 로그인 시스템
- [ ] 사용자별 즐겨찾기 저장 (DB) 
- [ ] 비밀번호 암호화 (bcrypt)

### 알림 기능
- [ ] 특정 종목 가격 도달 시 알림
- [ ] 테마 강세 알림
- [ ] 이메일 또는 푸시 알림

### 모바일 앱 (React Native)
- [ ] React Native 프로젝트 생성
- [ ] 기존 API 재사용
- [ ] iOS/Android 빌드

---

## 📅 예상 일정

| Phase | 예상 소요 시간 | 상태 |
|-------|--------------|------|
| Phase 1: 환경 구축 | 2-3일 | ✅ 거의 완료 |
| Phase 2: 백엔드 개발 | 1-2주 | ⏳ 대기 |
| Phase 3: 프론트엔드 개발 | 1-2주 | ⏳ 대기 |
| Phase 4: 데이터 초기화 | 1-2일 | ⏳ 대기 |
| Phase 5: 통합 테스트 | 3-5일 | ⏳ 대기 |
| Phase 6: 배포 | 2-3일 | ⏳ 대기 |
| **총 예상 기간** | **4-6주** | |

---

## 🎯 현재 진행 상황

- [x] 분석 문서 작성 완료
- [x] 설계 문서 작성 완료
- [/] 개발 환경 구축 진행 중
  - [x] GitHub 원격 저장소 연결 완료
  - [x] Docker Desktop 설치 완료
  - [x] 한국투자증권 API 사용 신청 완료
  - [x] Docker Compose 설정 파일 작성 완료
  - [x] Backend/Frontend 기본 구조 생성 완료
  - [ ] Docker Compose 실행 및 테스트 ← **다음 단계**

---

**마지막 업데이트**: 2026-02-07
