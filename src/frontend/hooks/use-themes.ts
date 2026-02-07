import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api';

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

// 실시간 시세 조회 (60초마다 자동 갱신)
export function useStockQuote(code: string) {
    return useQuery({
        queryKey: ['quote', code],
        queryFn: () => api.getStockQuote(code),
        refetchInterval: 60000, // 60초마다 자동 갱신
        enabled: !!code,
    });
}

// 테마별 거래량 순위 조회 (60초마다 자동 갱신)
export function useVolumeRankByTheme() {
    return useQuery({
        queryKey: ['volume-rank-by-theme'],
        queryFn: api.getVolumeRankByTheme,
        refetchInterval: 60000, // 60초마다 자동 갱신
    });
}
