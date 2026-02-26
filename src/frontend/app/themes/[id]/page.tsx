'use client';

import { useVolumeRankByTheme } from '@/hooks/use-themes';
import { isMarketClosed } from '@/lib/utils';
import StockRow from '@/components/StockRow';
import Link from 'next/link';
import { useParams, useSearchParams } from 'next/navigation';
import { useState, Suspense, useEffect } from 'react';

type MarketType = 'ALL' | 'KRX' | 'NXT';

const MARKET_BUTTONS: { key: MarketType; label: string; activeClass: string }[] = [
    { key: 'ALL', label: '통합', activeClass: 'bg-green-400 text-white hover:bg-green-500' },
    { key: 'KRX', label: 'KRX', activeClass: 'bg-blue-600 text-white hover:bg-blue-700' },
    { key: 'NXT', label: 'NXT', activeClass: 'bg-slate-600 text-white hover:bg-slate-700' },
];

function ThemeContent() {
    const params = useParams();
    const searchParams = useSearchParams();
    const themeName = decodeURIComponent(params.id as string);

    // URL에서 market 파라미터 읽기
    const marketParam = searchParams.get('market') as MarketType | null;

    // 초기 상태 설정
    const [marketType, setMarketType] = useState<MarketType>('ALL');
    const [isInitialized, setIsInitialized] = useState(false);

    useEffect(() => {
        if (!isInitialized) {
            setMarketType((marketParam as MarketType) || 'ALL');
            setIsInitialized(true);
        }
    }, [marketParam, isInitialized]);


    const { data: volumeRankings, isLoading, error } = useVolumeRankByTheme(marketType);

    if (!isInitialized) return null; // Prevent hydration mismatch

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

    const totalTradingValue = stocks.reduce(
        (sum: number, stock) => sum + stock.trading_value, 0
    );

    const formatTotalValue = (value: number) => {
        if (value >= 100000000) {
            return `${Math.floor(value / 100000000).toLocaleString('ko-KR')}억`;
        }
        return `${value.toLocaleString('ko-KR')}`;
    };

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
                <div className="flex items-center gap-3">
                    <h1 className="text-2xl font-bold text-gray-900">{themeName}</h1>
                    <span className="text-gray-300 text-xl">|</span>
                    <p className="text-gray-500 text-sm">실시간 거래대금 상위 종목</p>
                </div>
            </div>

            {/* 종목 목록 */}
            <div className="bg-white rounded-lg shadow-sm p-4">
                <div className="flex items-center justify-between mb-4">
                    <h2 className="text-base font-bold text-gray-900">
                        종목 목록 ({stocks.length}개)
                    </h2>
                    <div className="flex items-center gap-2">
                        {/* 거래대금 합계 배지 */}
                        {stocks.length > 0 && (
                            <div className="text-xs text-blue-600 font-semibold whitespace-nowrap bg-blue-50 px-2 py-1 rounded">
                                {formatTotalValue(totalTradingValue)}
                            </div>
                        )}
                        {/* 통합/KRX/NXT 3단 토글 */}
                        <div className="flex gap-1">
                            {MARKET_BUTTONS.map((btn) => (
                                <button
                                    key={btn.key}
                                    onClick={() => setMarketType(btn.key)}
                                    className={`text-xs font-semibold px-2 py-1 rounded transition-colors ${marketType === btn.key
                                        ? btn.activeClass
                                        : 'bg-gray-100 text-gray-500 hover:bg-gray-200'
                                        }`}
                                >
                                    {btn.label}
                                </button>
                            ))}
                        </div>
                    </div>
                </div>
                <div className="divide-y divide-gray-100">
                    {stocks.map((stock, index) => (
                        <StockRow key={stock.code} stock={stock} rank={index + 1} />
                    ))}
                </div>
            </div>

            {/* 자동 갱신 안내 */}
            <div className="mt-4 text-center text-sm text-gray-500">
                {isMarketClosed()
                    ? "💡 장 종료 후에는 최종 데이터를 표시합니다"
                    : "💡 데이터는 3초마다 자동으로 갱신됩니다"}
            </div>

        </div>
    );
}

export default function ThemePage() {
    return (
        <Suspense fallback={
            <div className="text-center py-12">
                <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
                <p className="mt-4 text-gray-600">로딩 중...</p>
            </div>
        }>
            <ThemeContent />
        </Suspense>
    );
}
