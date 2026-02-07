'use client';

import { useStockQuote } from '@/hooks/use-themes';
import { StockInTheme } from '@/types';

interface StockRowProps {
    stock: StockInTheme;
}

function StockRow({ stock }: StockRowProps) {
    const { data: quote, isLoading } = useStockQuote(stock.code);

    const priceColor = quote
        ? quote.change_rate > 0
            ? 'text-red-600'
            : quote.change_rate < 0
                ? 'text-blue-600'
                : 'text-gray-900'
        : 'text-gray-900';

    return (
        <tr className="border-b hover:bg-gray-50">
            <td className="px-4 py-3 font-medium text-gray-900">{stock.name}</td>
            <td className="px-4 py-3 text-gray-600">{stock.code}</td>
            <td className={`px-4 py-3 ${priceColor} font-semibold`}>
                {isLoading ? (
                    <span className="text-gray-400">로딩중...</span>
                ) : quote ? (
                    `${quote.current_price.toLocaleString()}원`
                ) : (
                    <span className="text-gray-400">-</span>
                )}
            </td>
            <td className={`px-4 py-3 ${priceColor} font-semibold`}>
                {quote && quote.change_rate !== 0 ? (
                    <>
                        {quote.change_rate > 0 ? '▲' : '▼'} {Math.abs(quote.change_price).toLocaleString()}원
                        <span className="text-sm ml-1">
                            ({quote.change_rate > 0 ? '+' : ''}{quote.change_rate.toFixed(2)}%)
                        </span>
                    </>
                ) : quote ? (
                    <span className="text-gray-400">-</span>
                ) : (
                    <span className="text-gray-400">-</span>
                )}
            </td>
            <td className="px-4 py-3">
                <div className="flex items-center">
                    <div className="w-16 h-2 bg-gray-200 rounded-full overflow-hidden">
                        <div
                            className="h-full bg-blue-500"
                            style={{ width: `${stock.weight * 10}%` }}
                        />
                    </div>
                    <span className="ml-2 text-sm text-gray-600">{stock.weight}/10</span>
                </div>
            </td>
        </tr>
    );
}

interface StockTableProps {
    stocks: StockInTheme[];
}

export default function StockTable({ stocks }: StockTableProps) {
    if (!stocks || stocks.length === 0) {
        return (
            <div className="text-center py-8 text-gray-500">
                등록된 종목이 없습니다.
            </div>
        );
    }

    return (
        <div className="bg-white rounded-lg shadow overflow-hidden">
            <table className="w-full">
                <thead className="bg-gray-100 border-b">
                    <tr>
                        <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">종목명</th>
                        <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">코드</th>
                        <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">현재가</th>
                        <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">등락</th>
                        <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">가중치</th>
                    </tr>
                </thead>
                <tbody>
                    {stocks.map((stock) => (
                        <StockRow key={stock.code} stock={stock} />
                    ))}
                </tbody>
            </table>
        </div>
    );
}
