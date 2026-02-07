'use client';

import { useEffect, useState } from 'react';

export default function Home() {
    const [apiStatus, setApiStatus] = useState<string>('확인 중...');
    const [apiData, setApiData] = useState<any>(null);

    useEffect(() => {
        // Backend API 헬스체크
        fetch('http://localhost:8000/health')
            .then(res => res.json())
            .then(data => {
                setApiStatus('✅ 연결됨');
                setApiData(data);
            })
            .catch(error => {
                setApiStatus('❌ 연결 실패');
                console.error('API 연결 오류:', error);
            });
    }, []);

    return (
        <main style={{ padding: '2rem', fontFamily: 'system-ui, sans-serif' }}>
            <h1>📊 StockThemeBoard</h1>
            <p>주식 테마별 종목 실시간 모니터링 대시보드</p>

            <div style={{
                marginTop: '2rem',
                padding: '1rem',
                border: '1px solid #ddd',
                borderRadius: '8px',
                backgroundColor: '#f9f9f9'
            }}>
                <h2>🔌 Backend API 상태</h2>
                <p><strong>상태:</strong> {apiStatus}</p>
                {apiData && (
                    <div>
                        <p><strong>환경:</strong> {apiData.environment}</p>
                        <p><strong>상태:</strong> {apiData.status}</p>
                    </div>
                )}
            </div>

            <div style={{ marginTop: '2rem' }}>
                <h2>📋 다음 단계</h2>
                <ul>
                    <li>✅ Docker Compose 환경 구축 완료</li>
                    <li>⏳ 데이터베이스 모델 설계</li>
                    <li>⏳ 한국투자증권 API 연동</li>
                    <li>⏳ REST API 구현</li>
                    <li>⏳ WebSocket 실시간 연동</li>
                </ul>
            </div>
        </main>
    );
}
