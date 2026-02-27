'use client';

import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api';
import { IndexQuote } from '@/types';

export default function IndexHeader() {
    const { data, isLoading, error } = useQuery({
        queryKey: ['indices'],
        queryFn: api.getIndices,
        refetchInterval: 30 * 1000, // 30초마다 갱신
    });

    if (isLoading) {
        return (
            <div className="bg-gray-900 text-white py-2 px-4 shadow-inner">
                <div className="container mx-auto flex gap-6">
                    <div className="h-4 w-32 bg-gray-700 animate-pulse rounded"></div>
                    <div className="h-4 w-32 bg-gray-700 animate-pulse rounded"></div>
                </div>
            </div>
        );
    }

    if (error || !data) {
        return null;
    }

    return (
        <div className="bg-gray-900 text-white py-2 px-4 shadow-inner border-b border-gray-800">
            <div className="container mx-auto flex items-center gap-6 text-sm font-medium">
                {data.items.map((item) => (
                    <IndexItem key={item.index_code} item={item} />
                ))}
                <div className="ml-auto text-[10px] text-gray-500 hidden sm:block">
                    마지막 갱신: {new Date(data.items[0].timestamp).toLocaleTimeString()}
                </div>
            </div>
        </div>
    );
}

function IndexItem({ item }: { item: IndexQuote }) {
    const isUp = item.change_price > 0;
    const isDown = item.change_price < 0;

    const indexName = item.index_code === '0001' ? '코스피' : '코스닥';

    return (
        <div className="flex items-center gap-3 whitespace-nowrap">
            <span className="text-gray-400 font-bold tracking-tight">{indexName}</span>
            <span className="font-semibold tabular-nums">
                {item.current_price.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </span>
            <span className={`text-xs font-bold ${isUp ? 'text-red-400' : isDown ? 'text-blue-400' : 'text-gray-400'}`}>
                {isUp ? '▲' : isDown ? '▼' : '-'}
                {Math.abs(item.change_price).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </span>
        </div>
    );
}
