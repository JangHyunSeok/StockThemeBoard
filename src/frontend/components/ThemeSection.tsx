'use client';
import { StockRanking } from '@/types';
import { useVolumeRankByTheme } from '@/hooks/use-themes';
import StockRow from '@/components/StockRow';
import Link from 'next/link';

interface ThemeSectionProps {
    themeName: string;
}

export default function ThemeSection({ themeName }: ThemeSectionProps) {
    const { data: allRankings, isLoading, error } = useVolumeRankByTheme();

    if (error) return null;
    if (isLoading) {
        return (
            <div className="bg-white rounded-lg shadow-sm p-4">
                <div className="animate-pulse">
                    <div className="h-5 bg-gray-200 rounded w-1/2 mb-3"></div>
                    <div className="space-y-2">
                        {[1, 2, 3, 4].map((i) => (
                            <div key={i} className="h-10 bg-gray-100 rounded"></div>
                        ))}
                    </div>
                </div>
            </div>
        );
    }

    if (!allRankings) return null;

    // 해당 테마의 종목들 (최대 4개만 표시)
    const themeStocks: StockRanking[] = (allRankings[themeName] || []).slice(0, 4);

    if (themeStocks.length === 0) return null;

    // 총 거래대금 계산
    const totalTradingValue = themeStocks.reduce((sum: number, stock: StockRanking) => sum + stock.trading_value, 0);

    const formatTotalValue = (value: number) => {
        if (value >= 100000000) { // 1억 이상
            // 소수점 절사 (내림)하여 정수로만 표시
            return `${Math.floor(value / 100000000).toLocaleString('ko-KR')}억`;
        }
        return `${value.toLocaleString('ko-KR')}`;
    };

    return (
        <Link href={`/themes/${encodeURIComponent(themeName)}`}>
            <div className="bg-white rounded-lg shadow-sm p-4 hover:shadow-md transition-shadow border border-gray-200 cursor-pointer">
                <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                        <h2 className="text-base font-bold text-gray-900 leading-tight">{themeName}</h2>
                    </div>
                    <div className="text-xs text-blue-600 font-semibold whitespace-nowrap ml-2 bg-blue-50 px-2 py-1 rounded">
                        {formatTotalValue(totalTradingValue)}
                    </div>
                </div>

                <div className="divide-y divide-gray-100">
                    {themeStocks.map((stock: StockRanking, index: number) => (
                        <StockRow key={stock.code} stock={stock} rank={index + 1} />
                    ))}
                </div>
            </div>
        </Link>
    );
}
