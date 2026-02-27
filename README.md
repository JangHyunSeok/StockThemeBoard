# 📊 StockThemeBoard

한국투자증권 OpenAPI를 활용한 **실시간 거래대금 상위 종목 모니터링 대시보드**

> 🌐 **데모**: https://stock.hayoone.com

## 🎯 프로젝트 개요

StockThemeBoard는 주식 테마별로 **실시간 거래대금 상위 종목**을 자동으로 수집하고 모니터링할 수 있는 웹 애플리케이션입니다. 한국투자증권 OpenAPI를 통해 실시간 시세와 거래량 데이터를 가져와 테마별로 분류하여 보여줍니다.

### ✨ 주요 기능

- 📊 **코스피/코스닥 지수 표시** - 상단바에 지수 현재가·등락률 실시간 표시 (30초 갱신)
- 🔥 **실시간 거래대금 상위 종목 조회** - KIS API를 통해 거래 활발한 종목 자동 수집
- 🏷️ **테마별 자동 분류** - KIS 업종명 기반 분류 및 **섹터 오버라이드 맵**으로 정밀 보정
- 📈 **실시간 시세 표시** - 현재가, 등락률, 거래대금 실시간 업데이트 (60초 자동 갱신)
- 🕯️ **캔들 차트** - 종목별 미니 캔들 차트 (고가/저가/시가/현재가 시각화)
- 🌏 **멀티 마켓 지원** - KRX / NXT / ALL(통합) 마켓 토글
- ⏰ **스마트 마켓 시간 처리** - KRX(09:00-20:00), NXT/ALL(08:00-20:00) 자동 구분
- 📱 **모바일 최적화** - 2열 그리드 레이아웃으로 모바일 친화적
- ⚡ **빠른 응답** - Redis 캐싱으로 API 응답 속도 향상
- 🎨 **직관적인 UI** - 상승(빨강)/하락(파랑) 색상 구분

## 🛠️ 기술 스택

### Backend
- **Python 3.11** - 프로그래밍 언어
- **FastAPI** - 비동기 웹 프레임워크
- **PostgreSQL 16** - 관계형 데이터베이스
- **Redis 7** - API 응답 캐싱 및 토큰 저장
- **SQLAlchemy 2.0** - 비동기 ORM
- **Alembic** - 데이터베이스 마이그레이션
- **httpx** - 비동기 HTTP 클라이언트 (KIS API 호출)

### Frontend
- **Next.js 14** - React 프레임워크 (App Router)
- **TypeScript** - 타입 안전성
- **Tailwind CSS** - 유틸리티 기반 스타일링
- **React Query (TanStack Query)** - 서버 상태 관리 및 캐싱
- **fetch API** - HTTP 클라이언트
- **date-holidays** - 공휴일 및 영업일 계산

### Infrastructure
- **Docker & Docker Compose** - 컨테이너화
- **Nginx** - 리버스 프록시 및 HTTPS 처리
- **Let's Encrypt (Certbot)** - 자동 SSL 인증서 발급/갱신
- **Portainer** - Docker 컨테이너 모니터링 UI (포트 9000)
- **PostgreSQL Container** - 데이터베이스
- **Redis Container** - 캐시 서버

### External API
- **한국투자증권 OpenAPI (KIS)** - 실시간 주식 시세, 거래량 순위, 업종 지수 데이터

## 📁 프로젝트 구조

```
StockThemeBoard/
├── doc/                              # 📚 문서
│   ├── 01. 분석/
│   │   └── 분석자료.md
│   ├── 02. 설계/
│   │   └── 설계문서.md
│   └── 03. 개발/
│       ├── 개발 ToDo.md
│       └── 프로젝트_구조.md
│
├── src/
│   ├── backend/                      # 🔧 Backend (FastAPI)
│   │   ├── app/
│   │   │   ├── api/v1/              # REST API 엔드포인트
│   │   │   │   ├── themes.py        # 테마 API
│   │   │   │   ├── stocks.py        # 종목 API (시세 조회)
│   │   │   │   ├── rankings.py      # 거래량 순위 API
│   │   │   │   ├── indices.py       # 코스피/코스닥 지수 API ← NEW
│   │   │   │   └── rankings_test.py # 테스트용 더미 API
│   │   │   ├── models/              # SQLAlchemy 모델
│   │   │   │   ├── theme.py
│   │   │   │   ├── stock.py
│   │   │   │   └── theme_stock.py
│   │   │   ├── schemas/             # Pydantic 스키마
│   │   │   │   └── index.py         # 지수 스키마 ← NEW
│   │   │   ├── services/            # 비즈니스 로직
│   │   │   │   ├── kis_client.py   # KIS API 클라이언트
│   │   │   │   └── redis_client.py # Redis 캐싱
│   │   │   └── utils/
│   │   │       └── business_day.py  # 영업일/마켓 시간 판별
│   │   ├── alembic/                 # 데이터베이스 마이그레이션
│   │   ├── scripts/                 # 유틸리티 스크립트
│   │   │   └── seed_data.py        # 초기 데이터 생성
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   │
│   └── frontend/                     # 🎨 Frontend (Next.js)
│       ├── app/
│       │   ├── page.tsx             # 홈 (테마별 TOP 4 종목)
│       │   ├── themes/[id]/
│       │   │   └── page.tsx         # 테마 상세 (TOP 15 종목)
│       │   ├── layout.tsx           # 지수 헤더 포함 글로벌 레이아웃
│       │   └── globals.css
│       ├── components/
│       │   ├── IndexHeader.tsx      # 코스피/코스닥 지수 상단바 ← NEW
│       │   ├── ThemeSection.tsx     # 테마 섹션 컴포넌트
│       │   └── StockRow.tsx         # 종목 행 (캔들 차트 포함)
│       ├── hooks/
│       │   └── use-themes.ts        # React Query 훅
│       ├── lib/
│       │   ├── api.ts               # API 클라이언트
│       │   └── query-provider.tsx   # React Query 설정
│       ├── types/
│       │   └── index.ts             # TypeScript 타입
│       ├── next.config.js           # API 프록시 rewrite 설정
│       ├── package.json
│       └── Dockerfile
│
├── nginx/                           # Nginx 설정
│   └── conf.d/
│       └── default.conf
├── certbot/                         # Let's Encrypt 인증서
├── docker-compose.yml               # Docker Compose 설정 (Nginx/Certbot/Portainer 포함)
├── .env                             # 환경변수
└── README.md
```

## 🚀 시작하기

### 사전 요구사항
- Docker Desktop (Windows/Mac) 또는 Docker Engine (Linux)
- Docker Compose
- 한국투자증권 계좌 및 OpenAPI Key

### 1. 저장소 클론
```bash
git clone https://github.com/YOUR_USERNAME/StockThemeBoard.git
cd StockThemeBoard
```

### 2. 환경변수 설정
`.env` 파일에 한투 API 키 입력:
```env
# 한국투자증권 OpenAPI 설정
KIS_APP_KEY=your_app_key_here
KIS_APP_SECRET=your_app_secret_here
KIS_ACCOUNT_NUMBER=your_account_number
KIS_BASE_URL=https://openapi.koreainvestment.com:9443

# 데이터베이스 설정
DATABASE_URL=postgresql+asyncpg://stockuser:stockpass@postgres:5432/stocktheme

# Redis 설정
REDIS_URL=redis://redis:6379/0
```

### 3. 실행 방법 (선택)

#### 옵션 A: 로컬 실행 (권장 - 빠르고 안정적)
```bash
# Frontend (새 터미널)
cd src/frontend
npm install
npm run dev
# 접속: http://localhost:3000
# 모바일/외부 접속: http://[PC_IP]:3000 (Proxy 설정 완료)
```

#### 옵션 B: Docker Compose 실행 (백엔드/DB 필수)
```bash
# 모든 서비스 시작
docker-compose up -d

# 로그 확인
docker-compose logs -f
```

### 4. 데이터베이스 마이그레이션
```bash
# Backend 컨테이너 접속
docker exec -it stocktheme-backend /bin/sh

# 마이그레이션 실행
alembic upgrade head

# (선택) 초기 데이터 생성
python scripts/seed_data.py
```

### 5. 접속
- **Frontend**: http://localhost
- **Backend API**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/docs
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

## 📖 API 문서

### Backend API 엔드포인트

#### 지수 API ← NEW
- `GET /api/v1/indices/current` - **코스피/코스닥 현재 지수 조회**
  - KIS API TR ID: `FHKUP03500100`
  - 응답 예시: `{ items: [{ index_code: "0001", current_price: 2600.00, change_price: -12.5, change_rate: -0.48 }] }`

#### 거래량 순위 API
- `GET /api/v1/rankings/volume-rank-by-theme` - 테마별 거래대금 상위 종목 (실시간)
  - `market` 파라미터: `KRX` (09:00-20:00), `NXT` (08:00-20:00), `ALL` (통합, 08:00-20:00)

#### 종목 API
- `GET /api/v1/stocks/{code}/quote` - **실시간 시세 조회**

#### 테마 API
- `GET /api/v1/themes` - 테마 목록 조회
- `GET /api/v1/themes/{id}` - 테마 상세 조회 (종목 포함)

자세한 API 명세는 http://localhost:8000/docs (Swagger UI) 에서 확인 가능합니다.

## 🎨 주요 화면

### 최상단 지수 바
- **코스피 / 코스닥** 현재가, 전일대비, 등락률 실시간 표시
- 30초마다 자동 갱신
- 상승 🔴 / 하락 🔵 색상 구분

### 메인 화면
- **KRX / NXT / ALL** 마켓 토글
- 18개 테마별로 거래대금 상위 4개 종목 표시
- 2x2 그리드: 종목명/등락률, 현재가/거래대금, 미니 캔들 차트
- 모바일: 1~2열, 데스크톱: 3열 그리드
- 60초마다 자동 갱신

### 테마 상세 화면
- 해당 테마의 거래대금 상위 15개 종목
- 실시간 시세 및 등락률
- 순위 및 캔들 차트 표시

## 🔑 한국투자증권 OpenAPI 발급

1. [한국투자증권 홈페이지](https://securities.koreainvestment.com/) 접속
2. 계좌 개설 (모의투자 또는 실전투자)
3. [KIS Developers](https://apiportal.koreainvestment.com/) 접속
4. App Key/Secret 발급
5. `.env` 파일에 입력

## 📅 개발 완료 현황

- [x] **Phase 1**: Docker 환경 구축
  - [x] Docker Compose 설정 (Nginx, Certbot, Portainer 포함)
  - [x] PostgreSQL, Redis 컨테이너
  - [x] Backend/Frontend Dockerfile
  - [x] HTTPS (Let's Encrypt) 자동 발급/갱신

- [x] **Phase 2**: 데이터베이스 모델링
  - [x] SQLAlchemy 모델 (Theme, Stock, ThemeStock)
  - [x] Alembic 마이그레이션 설정
  - [x] 초기 데이터 생성 스크립트

- [x] **Phase 3**: Backend API 개발
  - [x] FastAPI 프로젝트 구조
  - [x] Theme/Stock CRUD API
  - [x] 한투 API 클라이언트 (OAuth2, 시세 조회, 거래량 순위)
  - [x] **코스피/코스닥 지수 조회 API** (`FHKUP03500100`)
  - [x] Redis 캐싱 (토큰 24시간, 시세 60초)
  - [x] 마켓 시간 자동 판별 (KRX/NXT/ALL)
  - [x] 섹터 오버라이드 맵 (반도체, 조선, 원자력 등 18개 섹터)

- [x] **Phase 4**: Frontend 개발
  - [x] Next.js 14 App Router 설정
  - [x] React Query 데이터 페칭
  - [x] **코스피/코스닥 지수 상단바** (30초 갱신)
  - [x] **KRX / NXT / ALL 마켓 토글**
  - [x] 실시간 거래대금 상위 종목 화면 (60초 갱신)
  - [x] 테마별 TOP 4/15 종목 표시
  - [x] **미니 캔들 차트** (고가/저가/시가/현재가)
  - [x] Tailwind CSS 반응형 디자인

- [ ] **Phase 5**: 추가 기능 (예정)
  - [ ] 사용자 인증/로그인
  - [ ] 즐겨찾기 기능
  - [ ] WebSocket 실시간 업데이트

## 🧪 테스트

### Backend 테스트
```bash
# Swagger UI에서 테스트
open http://localhost:8000/docs

# 시세 조회 테스트
curl http://localhost:8000/api/v1/stocks/005930/quote

# 거래량 순위 테스트
curl http://localhost:8000/api/v1/rankings/volume-rank-by-theme-test
```

### Frontend 테스트
```bash
# 브라우저에서 접속
open http://localhost
```

## ⚠️ 알려진 이슈

### KIS API 관련 이슈 해결
- **주말/공휴일 대응**: `holidays` 라이브러리와 Hybrid 로직(DB+실시간)을 사용하여 365일 중단 없는 서비스 제공.
- **장 시간**: KRX(09:00-20:00), NXT/ALL(08:00-20:00) 구간별 서비스 제공.
- **API 속도**: Redis 캐싱(3초) 및 병렬 처리로 응답 속도 최적화.
- **지수 조회 TR ID**: `FHKUP03500100` (업종기간별시세), `FID_COND_MRKT_DIV_CODE: U` 사용.

### 해결 방법
- 평일 장중: 실시간 API + Redis 캐시(60초)
- 휴일/장마감: DB 저장 데이터 반환

## 🤝 기여

이슈 및 풀 리퀘스트는 언제든 환영합니다!

## 📝 라이선스

MIT License

## 👨‍💻 개발자

**장현석** - [GitHub Profile](https://github.com/JangHyunSeok)

---

**Last Updated**: 2026-02-27

**Version**: 1.4.0 (코스피/코스닥 지수 표시 추가)