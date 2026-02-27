import type { Metadata } from 'next';
import { QueryProvider } from '@/lib/query-provider';
import IndexHeader from '@/components/IndexHeader';
import './globals.css';

export const metadata: Metadata = {
    title: 'StockThemeBoard',
    description: '주식 테마별 종목 시세 모니터링 대시보드',
};

export default function RootLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <html lang="ko">
            <body className="bg-gray-50">
                <QueryProvider>
                    {/* 상단 고정 영역: 지수 바 + 로고 헤더 */}
                    <div className="sticky top-0 z-50">
                        <IndexHeader />
                        <header className="bg-white shadow-sm border-b">
                            <div className="container mx-auto px-4 py-3">
                                <h1 className="text-2xl font-bold text-gray-900">
                                    📊 StockThemeBoard
                                </h1>
                                <p className="text-sm text-gray-600">주식 테마별 종목 시세 모니터링</p>
                            </div>
                        </header>
                    </div>
                    <main className="container mx-auto px-4 py-6">
                        {children}
                    </main>
                </QueryProvider>
            </body>
        </html>
    );
}
