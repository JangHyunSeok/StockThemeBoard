"""
Let's Encrypt 인증서 초기 발급 스크립트 (Python 버전 - 아나콘다 프롬프트용)
사용법: python scripts/init-letsencrypt.py
프로젝트 루트(docker-compose.yml 위치)에서 실행할 것
"""

import os
import sys
import shutil
import subprocess
import time
import urllib.request
from pathlib import Path

# ──────────────────────────────────────────────
DOMAIN  = "stock.hayoone.com"
EMAIL   = "love2aska@gmail.com"
STAGING = False   # 테스트 시 True, 실제 발급 시 False
# ──────────────────────────────────────────────

def run(cmd, check=True):
    """명령어 실행 (리스트 형태)"""
    print(f"  $ {' '.join(cmd)}")
    result = subprocess.run(cmd, check=check)
    return result

def download(url, dest):
    if not Path(dest).exists():
        print(f"  다운로드: {dest}")
        urllib.request.urlretrieve(url, dest)
    else:
        print(f"  이미 존재: {dest}")

def step(n, total, msg):
    print(f"\n[{n}/{total}] {msg}")

# ─────────────────────────────────────────────────────────────
print("=" * 48)
print(" Let's Encrypt 인증서 초기 발급 스크립트")
print(f" 도메인: {DOMAIN}")
print("=" * 48)

# Step 1: certbot 디렉토리 생성
step(1, 6, "certbot 디렉토리 생성...")
Path("certbot/conf").mkdir(parents=True, exist_ok=True)
Path("certbot/www").mkdir(parents=True, exist_ok=True)
print("  완료")

# Step 2: SSL 파라미터 다운로드
step(2, 6, "SSL 파라미터 다운로드...")
download(
    "https://raw.githubusercontent.com/certbot/certbot/master/certbot-nginx/certbot_nginx/_internal/tls_configs/options-ssl-nginx.conf",
    "certbot/conf/options-ssl-nginx.conf"
)
download(
    "https://raw.githubusercontent.com/certbot/certbot/master/certbot/certbot/ssl-dhparams.pem",
    "certbot/conf/ssl-dhparams.pem"
)

# Step 3: HTTP 전용 설정이 활성화되어 있는지 확인 후 Nginx 시작
step(3, 6, "Nginx(HTTP 설정) 시작...")
conf_path = Path("nginx/conf.d/default.conf")
conf_content = conf_path.read_text(encoding="utf-8")
if "listen 443" in conf_content:
    print("  → SSL 설정 감지됨. HTTP 전용으로 복구...")
    http_only_conf = f"""server {{
    listen 80;
    server_name {DOMAIN};

    location /.well-known/acme-challenge/ {{
        root /var/www/certbot;
    }}

    location / {{
        proxy_pass http://frontend:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }}

    location /api/ {{
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
    }}
}}
"""
    conf_path.write_text(http_only_conf, encoding="utf-8")

run(["docker", "compose", "up", "-d", "nginx"])
print("  Nginx 준비 대기 (5초)...")
time.sleep(5)

# Step 4: Certbot으로 인증서 발급
step(4, 6, "Let's Encrypt 인증서 발급...")

pwd = str(Path.cwd()).replace("\\", "/")

certbot_cmd = [
    "docker", "run", "--rm",
    "-v", f"{pwd}/certbot/conf:/etc/letsencrypt",
    "-v", f"{pwd}/certbot/www:/var/www/certbot",
    "certbot/certbot", "certonly",
    "--webroot",
    "--webroot-path=/var/www/certbot",
    "--email", EMAIL,
    "--agree-tos",
    "--no-eff-email",
    "--force-renewal",
    "-d", DOMAIN,
]
if STAGING:
    certbot_cmd.append("--staging")
    print("  ⚠️  스테이징 모드 (테스트용 인증서)")

result = run(certbot_cmd, check=False)
if result.returncode != 0:
    print("\n❌ 인증서 발급 실패! 위 에러 메시지를 확인하세요.")
    print("   공통 원인:")
    print("   - 도메인 DNS가 이 서버를 가리키지 않음")
    print("   - 공유기 80 포트포워딩이 아직 Nginx(80)로 변경되지 않음")
    print("   - 방화벽에서 포트 80 차단")
    sys.exit(1)

print("  ✅ 인증서 발급 완료!")

# Step 5: HTTPS 설정으로 교체
step(5, 6, "HTTPS Nginx 설정으로 교체...")
shutil.copy("nginx/conf.d/default.conf", "nginx/conf.d/default.conf.backup")
shutil.copy("nginx/conf.d/default-ssl.conf", "nginx/conf.d/default.conf")
print("  ✅ HTTPS 설정 적용 완료")

# Step 6: Nginx 리로드
step(6, 6, "Nginx 리로드...")
run(["docker", "compose", "exec", "nginx", "nginx", "-s", "reload"])

print()
print("=" * 48)
print("✅ HTTPS 설정 완료!")
print()
print(f"  접속 주소: https://{DOMAIN}")
print("  HTTP → HTTPS 자동 리다이렉트 활성화")
print()
print("📌 다음 단계:")
print("  전체 서비스 시작: docker compose up -d")
print("=" * 48)
