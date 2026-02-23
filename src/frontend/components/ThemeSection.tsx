'use client';
import { StockRanking } from '@/types';
import { useVolumeRankByTheme } from '@/hooks/use-themes';
import StockRow from '@/components/StockRow';
import Link from 'next/link';
import { useState, useEffect } from 'react';

interface ThemeSectionProps {
    themeName: string;
}

type MarketType = 'ALL' | 'KRX' | 'NXT';

const MARKET_BUTTONS: { key: MarketType; label: string; activeClass: string }[] = [
    { key: 'ALL', label: '통합', activeClass: 'bg-green-400 text-white hover:bg-green-500' },
    { key: 'KRX', label: 'KRX', activeClass: 'bg-blue-600 text-white hover:bg-blue-700' },
    { key: 'NXT', label: 'NXT', activeClass: 'bg-slate-600 text-white hover:bg-slate-700' },
];

export default function ThemeSection({ themeName }: ThemeSectionProps) {
    const [marketType, setMarketType] = useState<MarketType>('ALL');

    useEffect(() => {
        setMarketType('ALL');
    }, []);

    const { data: allRankings, isLoading } = useVolumeRankByTheme(marketType);

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

    const themeStocks: StockRanking[] = [...(allRankings?.[themeName] || [])]
        .sort((a, b) => b.trading_value - a.trading_value)
        .slice(0, 4);

    const totalTradingValue = themeStocks.reduce(
        (sum: number, stock: StockRanking) => sum + stock.trading_value, 0
    );

    const formatTotalValue = (value: number) => {
        if (value >= 100000000) {
            return `${Math.floor(value / 100000000).toLocaleString('ko-KR')}억`;
        }
        return `${value.toLocaleString('ko-KR')}`;
    };

    return (
        <div className="bg-white rounded-lg shadow-sm p-4 hover:shadow-md transition-shadow border border-gray-200">
            <div className="flex items-start justify-between mb-3">
                <div className="flex-1">
                    <Link href={`/themes/${encodeURIComponent(themeName)}?market=${marketType}`}>
                        <h2 className="text-base font-bold text-gray-900 leading-tight hover:text-blue-600 cursor-pointer transition-colors">
                            {themeName}
                        </h2>
                    </Link>
                </div>

                {themeStocks.length > 0 && (
                    <div className="text-xs text-blue-600 font-semibold whitespace-nowrap ml-2 bg-blue-50 px-2 py-1 rounded">
                        {formatTotalValue(totalTradingValue)}
                    </div>
                )}

                {/* 통합/KRX/NXT 3단 토글 */}
                <div className="flex gap-1 ml-2">
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

            {themeStocks.length > 0 ? (
                <div className="divide-y divide-gray-100">
                    {themeStocks.map((stock: StockRanking, index: number) => (
                        <StockRow key={stock.code} stock={stock} rank={index + 1} />
                    ))}
                </div>
            ) : (
                <div className="text-center py-4 text-xs text-gray-400">
                    {marketType === 'NXT'
                        ? 'NXT 데이터는 20:00 이후 제공됩니다'
                        : '해당 업종 데이터가 없습니다'}
                </div>
            )}
        </div>
    );
}
