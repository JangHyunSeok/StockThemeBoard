'use client';

import { useVolumeRankByTheme } from '@/hooks/use-themes';
import StockRow from '@/components/StockRow';
import Link from 'next/link';
import { useParams } from 'next/navigation';

export default function ThemePage() {
    const params = useParams();
    const themeName = decodeURIComponent(params.id as string);

    const { data: volumeRankings, isLoading, error } = useVolumeRankByTheme();

    if (error) {
        return (
            <div className="text-center py-12">
                <p className="text-red-600 mb-4">❌ 데이터를 불러올 수 없습니다</p>
                <Link href="/" className="text-blue-600 hover:underline">
                    ← 메인으로 돌아가기
                </Link>
            </div>
        );
    }

    if (isLoading) {
        return (
            <div className="text-center py-12">
                <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
                <p className="mt-4 text-gray-600">데이터를 불러오는 중...</p>
            </div>
        );
    }

    if (!volumeRankings || !volumeRankings[themeName]) {
        return (
            <div className="text-center py-12">
                <p className="text-gray-600 mb-4">해당 테마를 찾을 수 없습니다</p>
                <Link href="/" className="text-blue-600 hover:underline">
                    ← 메인으로 돌아가기
                </Link>
            </div>
        );
    }

    // 해당 테마의 모든 종목 (최대 15개)
    const stocks = volumeRankings[themeName].slice(0, 15);

    return (
        <div>
            {/* 뒤로가기 */}
            <div className="mb-6">
                <Link href="/" className="inline-flex items-center text-blue-600 hover:underline">
                    <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                    </svg>
                    메인
                </Link>
            </div>

            {/* 테마 정보 */}
            <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
                <h1 className="text-3xl font-bold text-gray-900 mb-2">{themeName}</h1>
                <p className="text-gray-600">실시간 거래대금 상위 종목 (최대 15개)</p>
            </div>

            {/* 종목 목록 */}
            <div className="bg-white rounded-lg shadow-sm p-4">
                <h2 className="text-xl font-bold text-gray-900 mb-4">
                    종목 목록 ({stocks.length}개)
                </h2>
                <div className="divide-y divide-gray-100">
                    {stocks.map((stock, index) => (
                        <StockRow key={stock.code} stock={stock} rank={index + 1} />
                    ))}
                </div>
            </div>

            {/* 자동 갱신 안내 */}
            <div className="mt-4 text-center text-sm text-gray-500">
                💡 데이터는 60초마다 자동으로 갱신됩니다
            </div>
        </div>
    );
}
