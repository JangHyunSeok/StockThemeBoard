'use client';

import { StockRanking } from '@/types';
import { useEffect, useRef, useState } from 'react';

interface StockRowProps {
    stock: StockRanking;
    rank: number;
}

export default function StockRow({ stock, rank }: StockRowProps) {
    const [animationClass, setAnimationClass] = useState('');
    const prevPriceRef = useRef<number>(stock.current_price);
    const prevValueRef = useRef<number>(stock.trading_value);

    useEffect(() => {
        let timer: NodeJS.Timeout;

        // 가격 또는 거래대금 변경 감지
        if (prevPriceRef.current !== stock.current_price || prevValueRef.current !== stock.trading_value) {
            const isUp = stock.current_price > prevPriceRef.current || stock.trading_value > prevValueRef.current;
            const isDown = stock.current_price < prevPriceRef.current;

            if (isUp) {
                // setAnimationClass('animate-flash-up');
            } else if (isDown) {
                // setAnimationClass('animate-flash-down');
            }

            // 1초 후 애니메이션 클래스 제거 (다음 갱신을 위해)
            timer = setTimeout(() => {
                setAnimationClass('');
            }, 1000);

            // 이전 값 업데이트
            prevPriceRef.current = stock.current_price;
            prevValueRef.current = stock.trading_value;
        }

        return () => {
            if (timer) clearTimeout(timer);
        };
    }, [stock.current_price, stock.trading_value]);

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
        <div className={`py-1.5 px-2 hover:bg-gray-50 rounded border-b border-gray-50 last:border-0 transition-colors duration-300 ${animationClass}`}>
            <div className="flex items-center justify-between">
                {/* 좌측: 순위 및 종목명 */}
                <div className="flex items-center gap-2 flex-1 min-w-0">
                    <span className="text-xs font-bold text-gray-500 w-4">{rank}</span>
                    <span className="text-sm font-medium text-gray-900 truncate">{stock.name}</span>
                </div>

                {/* 우측: 가격 정보 */}
                <div className="flex items-center gap-3 text-right">
                    {/* 거래대금 */}
                    <div className="text-xs text-gray-500 font-medium">
                        {formatValue(stock.trading_value)}
                        {stock.trading_value_change_rate !== null && stock.trading_value_change_rate !== undefined && (
                            <span className="text-[10px] text-orange-500 ml-1">
                                ({stock.trading_value_change_rate.toFixed(0)}%)
                            </span>
                        )}
                    </div>

                    {/* 현재가 및 등락률 */}
                    <div className="flex flex-col items-end min-w-[60px]">
                        <span className={`text-xs font-semibold ${priceColor}`}>
                            {stock.current_price.toLocaleString()}
                        </span>
                        <span className={`text-[10px] ${priceColor}`}>
                            {stock.change_rate > 0 ? '+' : ''}{stock.change_rate.toFixed(2)}%
                        </span>
                    </div>
                </div>
            </div>
        </div>
    );
}
