# 📊 StockThemeBoard

한국투자증권 OpenAPI를 활용한 주식 테마별 종목 실시간 모니터링 대시보드

## 🎯 프로젝트 개요

StockThemeBoard는 주식 테마별로 종목을 분류하고, 거래량/거래대금 기준 상위 5개 종목을 실시간으로 모니터링할 수 있는 웹 애플리케이션입니다.

### 주요 기능
- ✅ 테마별 종목 분류 및 관리
- 📈 거래량 기준 TOP 5 종목 표시
- 💰 거래대금 기준 TOP 5 종목 표시
- 🔄 실시간 시세 자동 갱신 (WebSocket)
- ⭐ 사용자 관심 테마 즐겨찾기
- 📊 테마별 거래량/거래대금 차트 시각화

## 🛠️ 기술 스택

### Backend
- **Python 3.11+** - 프로그래밍 언어
- **FastAPI** - 비동기 웹 프레임워크
- **PostgreSQL 16+** - 관계형 데이터베이스
- **Redis 7+** - 캐싱 및 세션 관리
- **SQLAlchemy** - ORM
- **Alembic** - 데이터베이스 마이그레이션

### Frontend
- **Next.js 14+** - React 프레임워크
- **TypeScript** - 타입 안전성
- **Tailwind CSS** - 스타일링
- **shadcn/ui** - UI 컴포넌트
- **Zustand** - 상태 관리
- **Recharts** - 차트 라이브러리

### Infrastructure
- **Docker & Docker Compose** - 컨테이너화
- **Nginx** - 리버스 프록시
- **GitHub Actions** - CI/CD

### External API
- **한국투자증권 OpenAPI** - 실시간 주식 시세 데이터

## 📁 프로젝트 구조

```
StockThemeBoard/
├── doc/                          # 문서
│   ├── 01. 분석/
│   │   └── 분석자료.md           # 요구사항 분석 문서
│   ├── 02. 설계/
│   │   └── 설계문서.md           # 시스템 설계 문서
│   └── 03. 개발/
│       └── 개발 ToDo.md          # 개발 체크리스트
│
├── backend/                      # 백엔드 (예정)
│   ├── app/
│   ├── alembic/
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/                     # 프론트엔드 (예정)
│   ├── app/
│   ├── components/
│   ├── lib/
│   └── Dockerfile
│
├── docker-compose.yml           # Docker Compose 설정 (예정)
├── .gitignore
└── README.md
```

## 🚀 시작하기

### 사전 요구사항
- Python 3.11 이상
- Node.js 20 이상
- Docker & Docker Compose
- 한국투자증권 계좌 및 OpenAPI Key

### 1. 저장소 클론
```bash
git clone https://github.com/YOUR_USERNAME/StockThemeBoard.git
cd StockThemeBoard
```

### 2. 환경변수 설정
```bash
# backend/.env 파일 생성
cp backend/.env.example backend/.env

# 한투 API 키 설정
KIS_APP_KEY=your_app_key
KIS_APP_SECRET=your_app_secret
```

### 3. Docker Compose 실행
```bash
docker-compose up -d
```

### 4. 접속
- 프론트엔드: http://localhost:3000
- 백엔드 API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs

## 📖 문서

- [분석자료](./doc/01.%20분석/분석자료.md) - 요구사항 분석 및 시스템 개요
- [설계문서](./doc/02.%20설계/설계문서.md) - 시스템 아키텍처 및 기술 명세
- [개발 ToDo](./doc/03.%20개발/개발%20ToDo.md) - 개발 단계별 체크리스트

## 🔑 한국투자증권 OpenAPI 발급

1. [한국투자증권 홈페이지](https://securities.koreainvestment.com/) 접속
2. 계좌 개설 (모의투자 또는 실전투자)
3. [KIS Developers](https://apiportal.koreainvestment.com/) 접속
4. App Key/Secret 발급

## 📅 개발 로드맵

- [x] **Phase 0**: 분석 및 설계 (완료)
- [ ] **Phase 1**: 개발 환경 구축
- [ ] **Phase 2**: 백엔드 개발
- [ ] **Phase 3**: 프론트엔드 개발
- [ ] **Phase 4**: 데이터베이스 초기화
- [ ] **Phase 5**: 통합 테스트
- [ ] **Phase 6**: 배포

자세한 일정은 [개발 ToDo](./doc/03.%20개발/개발%20ToDo.md)를 참고하세요.

## 🤝 기여

이슈 및 풀 리퀘스트는 언제든 환영합니다!

## 📝 라이선스

MIT License

## 👨‍💻 개발자

**장현석** - [GitHub Profile](https://github.com/YOUR_USERNAME)

---

**Last Updated**: 2026-02-04
