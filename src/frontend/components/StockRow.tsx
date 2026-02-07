'use client';

import { StockRanking } from '@/types';

interface StockRowProps {
    stock: StockRanking;
    rank: number;
}

export default function StockRow({ stock, rank }: StockRowProps) {
    const priceColor = stock.change_rate > 0
        ? 'text-red-600'
        : stock.change_rate < 0
            ? 'text-blue-600'
            : 'text-gray-900';

    const formatValue = (value: number) => {
        if (value >= 100000000) { // 1억 이상
            return `${Math.floor(value / 100000000).toLocaleString()}억`;
        } else if (value >= 10000) { // 1만 이상
            return `${Math.floor(value / 10000).toLocaleString()}만`;
        }
        return value.toLocaleString();
    };

    return (
        <div className="py-3 px-2 hover:bg-gray-50 rounded">
            <div className="grid grid-cols-2 gap-2">
                {/* 좌측 상단: 종목명 */}
                <div className="font-medium text-gray-900 text-sm">
                    {rank}. {stock.name}
                </div>

                {/* 우측 상단: 등락률 */}
                <div className={`text-right font-bold text-sm ${priceColor}`}>
                    {stock.change_rate > 0 ? '▲' : stock.change_rate < 0 ? '▼' : ''}
                    {stock.change_rate > 0 ? '+' : ''}{stock.change_rate.toFixed(2)}%
                </div>

                {/* 좌측 하단: 현재가 */}
                <div className={`font-semibold text-sm ${priceColor}`}>
                    {stock.current_price.toLocaleString()}원
                </div>

                {/* 우측 하단: 거래대금 (천단위 콤마) */}
                <div className="text-right text-xs text-gray-600">
                    {formatValue(stock.trading_value)}
                </div>
            </div>
        </div>
    );
}
