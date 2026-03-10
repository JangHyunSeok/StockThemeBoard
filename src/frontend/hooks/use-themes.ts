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

// 테마별 거래량 순위 조회
export function useVolumeRankByTheme(market?: 'KRX' | 'NXT' | 'ALL') {
    const defaultMarket = market || 'ALL';

    // 마켓별 폴링 주기 — 백엔드 캐시 TTL 3초와 동일하게 통일
    // (웹소켓 도입 전까지 3초 갱신 유지)
    const getRefetchInterval = () => {
        if (isMarketClosed(defaultMarket)) return false;
        return 3000; // ALL / KRX / NXT 모두 3초
    };

    return useQuery({
        queryKey: ['volume-rank-by-theme', defaultMarket],
        queryFn: () => api.getVolumeRankByTheme(defaultMarket),
        refetchInterval: getRefetchInterval,
        refetchIntervalInBackground: false,
    });
}
