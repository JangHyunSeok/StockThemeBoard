/** @type {import('next').NextConfig} */
const nextConfig = {
    reactStrictMode: true,
    async rewrites() {
        return [
            {
                source: '/api/:path*',
                // 로컬 실행 시 127.0.0.1 대신 내부 IP(192.168.0.205) 사용 (Docker 네트워크 문제 회피)
                destination: process.env.NODE_ENV === 'production' ? 'http://backend:8000/api/:path*' : 'http://192.168.0.205:8000/api/:path*',
            },
        ];
    },
};

module.exports = nextConfig;
