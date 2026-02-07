import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api';
import { isMarketClosed } from '@/lib/utils';

// 테마 목록 조회
export function useThemes() {
    return useQuery({
        queryKey: ['themes'],
        queryFn: api.getThemes,
    });
}

// 테마 상세 조회 (종목 포함)
export function useTheme(id: string) {
    return useQuery({
        queryKey: ['theme', id],
        queryFn: () => api.getTheme(id),
        enabled: !!id, // id가 있을 때만 실행
    });
}

// 실시간 시세 조회 (평일: 60초마다 / 주말: 갱신 안 함)
export function useStockQuote(code: string) {
    return useQuery({
        queryKey: ['quote', code],
        queryFn: () => api.getStockQuote(code),
        refetchInterval: isMarketClosed() ? false : 60000, // 휴장일에는 자동 갱신 비활성화
        enabled: !!code,
    });
}

// 테마별 거래량 순위 조회 (평일: 10초마다 / 주말: 갱신 안 함)
export function useVolumeRankByTheme() {
    return useQuery({
        queryKey: ['volume-rank-by-theme'],
        queryFn: api.getVolumeRankByTheme,
        refetchInterval: isMarketClosed() ? false : 10000, // 휴장일에는 자동 갱신 비활성화
    });
}
