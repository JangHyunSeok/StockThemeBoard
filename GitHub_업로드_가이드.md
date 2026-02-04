# GitHub 업로드 가이드

## 📝 준비 완료된 파일
- ✅ `.gitignore` - Git 제외 파일 목록
- ✅ `README.md` - 프로젝트 설명 문서
- ✅ 분석/설계/개발 문서

---

## 🚀 GitHub에 올리는 방법

### 1️⃣ Git 저장소 초기화
터미널(또는 CMD)에서 프로젝트 폴더로 이동한 뒤 다음 명령어를 실행하세요:

```bash
cd d:\Workspace\StockThemeBoard

# Git 저장소 초기화
git init

# 모든 파일 스테이징
git add .

# 첫 커밋
git commit -m "Initial commit: 프로젝트 분석 및 설계 문서"
```

### 2️⃣ GitHub 저장소 생성
1. [GitHub](https://github.com) 로그인
2. 우측 상단 **"+"** 버튼 클릭 → **"New repository"** 선택
3. 저장소 정보 입력:
   - **Repository name**: `StockThemeBoard`
   - **Description**: `한국투자증권 OpenAPI를 활용한 주식 테마별 종목 실시간 모니터링 대시보드`
   - **Public** 또는 **Private** 선택
   - ⚠️ **"Initialize this repository with a README" 체크 해제** (이미 로컬에 README 있음)
4. **"Create repository"** 클릭

### 3️⃣ 원격 저장소 연결 및 푸시
GitHub에서 저장소 생성 후 나오는 명령어를 복사하거나, 다음 명령어를 실행하세요:

```bash
# 원격 저장소 추가 (YOUR_USERNAME을 본인 GitHub 아이디로 변경)
git remote add origin https://github.com/YOUR_USERNAME/StockThemeBoard.git

# 기본 브랜치를 main으로 설정
git branch -M main

# GitHub에 푸시
git push -u origin main
```

### 4️⃣ 인증
GitHub 인증 방법 선택:

**방법 A: Personal Access Token (권장)**
1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. "Generate new token" 클릭
3. `repo` 권한 체크
4. 생성된 토큰을 비밀번호 대신 입력

**방법 B: GitHub CLI 사용**
```bash
# GitHub CLI 설치 (https://cli.github.com/)
gh auth login

# 저장소 푸시
git push -u origin main
```

---

## ✅ 확인
푸시 완료 후 `https://github.com/YOUR_USERNAME/StockThemeBoard`로 이동하면 파일들이 업로드된 것을 확인할 수 있습니다!

---

## 🔄 이후 변경사항 푸시
프로젝트를 수정한 후 GitHub에 업데이트하려면:

```bash
# 변경 파일 스테이징
git add .

# 커밋
git commit -m "커밋 메시지"

# 푸시
git push
```

---

## 📌 예제: 완전한 명령어 흐름

```bash
# 1. 프로젝트 폴더로 이동
cd d:\Workspace\StockThemeBoard

# 2. Git 초기화
git init

# 3. 파일 추가
git add .

# 4. 첫 커밋
git commit -m "Initial commit: 프로젝트 분석 및 설계 문서"

# 5. 원격 저장소 연결 (YOUR_USERNAME 변경 필수!)
git remote add origin https://github.com/YOUR_USERNAME/StockThemeBoard.git

# 6. 브랜치 이름 설정
git branch -M main

# 7. GitHub에 푸시
git push -u origin main
```

---

## ⚠️ 주의사항
- `YOUR_USERNAME`을 본인의 GitHub 사용자명으로 꼭 변경하세요!
- `.env` 파일은 `.gitignore`에 포함되어 있어 업로드되지 않습니다 (API 키 보호)
- 처음 푸시 시 GitHub 인증이 필요합니다

---

**문제가 발생하면 에러 메시지를 공유해주세요!** 🚀
