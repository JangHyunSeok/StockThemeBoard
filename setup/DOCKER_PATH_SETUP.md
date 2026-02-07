# Docker 환경변수 설정 가이드

Docker Desktop은 설치되어 있지만 명령 프롬프트에서 `docker` 명령어를 인식하지 못하는 경우, 환경변수 PATH 설정이 필요합니다.

## 빠른 해결 방법

### 방법 1: Docker Desktop 재시작 (가장 간단)

1. Docker Desktop을 완전히 종료
2. Docker Desktop을 다시 실행
3. **새로운** 명령 프롬프트 창을 열기 (기존 창은 닫고)
4. `docker --version` 명령어 테스트

> [!IMPORTANT]
> Docker Desktop을 재시작한 후에는 **반드시 새로운 명령 프롬프트 창**을 열어야 합니다. 기존 창은 환경변수를 다시 읽지 않습니다.

### 방법 2: 환경변수 수동 설정

#### 1단계: Docker 설치 경로 확인

Docker Desktop의 기본 설치 경로는 다음 중 하나입니다:
- `C:\Program Files\Docker\Docker\resources\bin`
- `C:\Program Files\Docker\Docker\cli-plugins`

Windows 탐색기에서 다음 경로들이 존재하는지 확인하세요:
```
C:\Program Files\Docker\Docker\resources\bin\docker.exe
```

#### 2단계: 환경변수에 경로 추가

1. **시스템 속성 열기**
   - `Win + R` 키를 누르고 `sysdm.cpl` 입력 후 Enter
   - 또는 "제어판 > 시스템 > 고급 시스템 설정"

2. **환경 변수 버튼 클릭**
   - "고급" 탭에서 "환경 변수" 버튼 클릭

3. **Path 변수 편집**
   - "시스템 변수" 섹션에서 `Path` 찾기
   - `Path` 선택 후 "편집" 클릭

4. **Docker 경로 추가**
   - "새로 만들기" 클릭
   - 다음 경로들을 추가:
     ```
     C:\Program Files\Docker\Docker\resources\bin
     C:\ProgramData\DockerDesktop\version-bin
     ```

5. **확인하고 창 닫기**
   - 모든 창에서 "확인" 클릭

6. **명령 프롬프트 재시작**
   - 기존 명령 프롬프트를 모두 닫기
   - 새로운 명령 프롬프트 열기
   - `docker --version` 테스트

## 검증

새로운 명령 프롬프트에서 다음 명령어들을 실행하여 확인:

```bash
# Docker 버전 확인
docker --version

# Docker Compose 버전 확인
docker-compose --version

# Docker 실행 상태 확인
docker ps
```

정상 출력 예시:
```
C:\> docker --version
Docker version 24.0.7, build afdd53b

C:\> docker-compose --version
Docker Compose version v2.23.3-desktop.2

C:\> docker ps
CONTAINER ID   IMAGE     COMMAND   CREATED   STATUS    PORTS     NAMES
```

## 여전히 문제가 있다면

### PowerShell 사용 (대안)

명령 프롬프트 대신 PowerShell을 사용하면 더 잘 작동할 수 있습니다:

1. `Win + X` 키를 누르고 "Windows PowerShell (관리자)" 선택
2. 프로젝트 폴더로 이동:
   ```powershell
   cd d:\Workspace\StockThemeBoard
   ```
3. Docker 명령어 실행:
   ```powershell
   docker --version
   docker-compose up -d --build
   ```

### WSL2 확인

Docker Desktop은 WSL2를 사용합니다. WSL2가 제대로 설치되어 있는지 확인:

```bash
wsl --status
```

WSL2가 설치되지 않았다면:
```bash
wsl --install
```

### Docker Desktop 설정 확인

1. Docker Desktop 열기
2. 설정(톱니바퀴 아이콘) 클릭
3. "General" 탭에서:
   - ✅ "Use the WSL 2 based engine" 체크
   - ✅ "Add the *.docker.internal names to the host's /etc/hosts" 체크
4. "Apply & Restart" 클릭

## 다음 단계

환경변수 설정 후 Docker 명령어가 정상적으로 작동하면:

1. 새 명령 프롬프트 또는 PowerShell 열기
2. 프로젝트 폴더로 이동:
   ```bash
   cd d:\Workspace\StockThemeBoard
   ```
3. Docker Compose 실행:
   ```bash
   docker-compose up -d --build
   ```
