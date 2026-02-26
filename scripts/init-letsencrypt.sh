#!/bin/bash
# =============================================================================
# Let's Encrypt 인증서 초기 발급 스크립트
# 사용법: bash scripts/init-letsencrypt.sh
# =============================================================================

set -e  # 에러 발생 시 즉시 중단

DOMAIN="stock.hayoone.com"
EMAIL="love2aska@gmail.com"          # ← 본인 이메일로 변경 필요
STAGING=0                        # 테스트 시 1, 실제 발급 시 0

echo "========================================"
echo " Let's Encrypt 인증서 초기 발급 스크립트"
echo " 도메인: $DOMAIN"
echo "========================================"

# 1. certbot 디렉토리 생성
echo ""
echo "[1/6] certbot 디렉토리 생성..."
mkdir -p ./certbot/conf
mkdir -p ./certbot/www

# 2. Let's Encrypt 권장 SSL 파라미터 다운로드
echo ""
echo "[2/6] SSL 파라미터 다운로드..."
if [ ! -f ./certbot/conf/options-ssl-nginx.conf ]; then
    curl -s https://raw.githubusercontent.com/certbot/certbot/master/certbot-nginx/certbot_nginx/_internal/tls_configs/options-ssl-nginx.conf \
        -o ./certbot/conf/options-ssl-nginx.conf
fi

if [ ! -f ./certbot/conf/ssl-dhparams.pem ]; then
    curl -s https://raw.githubusercontent.com/certbot/certbot/master/certbot/certbot/ssl-dhparams.pem \
        -o ./certbot/conf/ssl-dhparams.pem
fi

# 3. 임시 자체서명 인증서 생성 (Nginx 최초 구동용)
echo ""
echo "[3/6] 임시 자체서명 인증서 생성 (Nginx 최초 구동용)..."
mkdir -p ./certbot/conf/live/$DOMAIN
if [ ! -f ./certbot/conf/live/$DOMAIN/privkey.pem ]; then
    docker run --rm \
        -v "$(pwd)/certbot/conf:/etc/letsencrypt" \
        certbot/certbot \
        certonly --standalone \
        --non-interactive \
        --agree-tos \
        -m $EMAIL \
        -d $DOMAIN \
        2>/dev/null || \
    openssl req -x509 -nodes -newkey rsa:2048 -days 1 \
        -keyout ./certbot/conf/live/$DOMAIN/privkey.pem \
        -out ./certbot/conf/live/$DOMAIN/fullchain.pem \
        -subj "/CN=localhost" 2>/dev/null || true
fi

# 4. Nginx(HTTP용) 먼저 시작
echo ""
echo "[4/6] Nginx(HTTP 설정) 시작..."
# HTTP 전용 설정이 활성화되어 있는지 확인
if [ -f ./nginx/conf.d/default-ssl.conf ]; then
    # SSL 설정이 있으면 임시로 제거 (아직 인증서 없으므로)
    mv ./nginx/conf.d/default-ssl.conf ./nginx/conf.d/default-ssl.conf.bak 2>/dev/null || true
fi

docker compose up -d nginx

echo "Nginx 준비 대기 (5초)..."
sleep 5

# 5. Certbot으로 실제 인증서 발급
echo ""
echo "[5/6] Let's Encrypt 인증서 발급..."

STAGING_FLAG=""
if [ $STAGING -eq 1 ]; then
    STAGING_FLAG="--staging"
    echo "⚠️  스테이징 모드 (테스트용 인증서)"
fi

docker run --rm \
    -v "$(pwd)/certbot/conf:/etc/letsencrypt" \
    -v "$(pwd)/certbot/www:/var/www/certbot" \
    certbot/certbot certonly \
    --webroot \
    --webroot-path=/var/www/certbot \
    $STAGING_FLAG \
    --email $EMAIL \
    --agree-tos \
    --no-eff-email \
    --force-renewal \
    -d $DOMAIN

echo "✅ 인증서 발급 완료!"

# 6. HTTPS 설정으로 교체하고 Nginx 재시작
echo ""
echo "[6/6] HTTPS 설정 적용..."

# SSL 설정으로 교체
cp ./nginx/conf.d/default.conf ./nginx/conf.d/default.conf.backup
cp ./nginx/conf.d/default-ssl.conf.bak ./nginx/conf.d/default-ssl.conf 2>/dev/null || \
    cp ./nginx/conf.d/default-ssl.conf ./nginx/conf.d/default.conf || true

# 실제로는 default.conf를 SSL 버전으로 교체
cp ./nginx/conf.d/default-ssl.conf ./nginx/conf.d/default.conf

# Nginx 설정 리로드
docker compose exec nginx nginx -s reload

echo ""
echo "========================================"
echo "✅ HTTPS 설정 완료!"
echo ""
echo "  접속 주소: https://$DOMAIN"
echo "  HTTP → HTTPS 자동 리다이렉트 활성화"
echo ""
echo "📌 다음 단계:"
echo "  전체 서비스 시작: docker compose up -d"
echo "========================================"
