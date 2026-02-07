import type { Metadata } from 'next';

export const metadata: Metadata = {
    title: 'StockThemeBoard',
    description: '주식 테마별 종목 실시간 모니터링 대시보드',
};

export default function RootLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <html lang="ko">
            <body>{children}</body>
        </html>
    );
}
