'use client';

import { useVolumeRankByTheme } from '@/hooks/use-themes';
import ThemeSection from '@/components/ThemeSection';
import { isMarketClosed } from '@/lib/utils';

export default function HomePage() {
    const { data: volumeRankings, isLoading, error } = useVolumeRankByTheme();

    if (error) {
        return (
            <div className="text-center py-12">
                <p className="text-red-600 mb-4">❌ 데이터를 불러올 수 없습니다</p>
                <p className="text-gray-600 text-sm">Backend API가 실행 중인지 확인하세요</p>
            </div>
        );
    }

    if (isLoading) {
        return (
            <div className="text-center py-12">
                <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
                <p className="mt-4 text-gray-600">실시간 데이터를 불러오는 중...</p>
            </div>
        );
    }

    if (!volumeRankings) {
        return (
            <div className="text-center py-12">
                <p className="text-gray-600">데이터가 없습니다.</p>
            </div>
        );
    }

    // 테마 목록 추출 - 백엔드에서 정렬된 순서 그대로 사용 (기타는 맨 마지막)
    const themeNames = Object.keys(volumeRankings);

    if (themeNames.length === 0) {
        return (
            <div className="text-center py-12">
                <p className="text-gray-600">등록된 테마가 없습니다.</p>
            </div>
        );
    }

    return (
        <div>
            {/* 반응형 그리드: 모바일 1열, 태블릿 2열, PC 3열 */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {themeNames.map((themeName) => (
                    <ThemeSection key={themeName} themeName={themeName} />
                ))}
            </div>

            {isMarketClosed('ALL') ? (
                <div className="mt-4 text-center text-xs text-gray-500">
                    💡 한국거래소 장 종료 후에는 대체거래소 및 최종 데이터를 표시합니다
                </div>
            ) : (
                <div className="mt-4 text-center text-xs text-gray-500">
                    💡 거래대금 상위 종목이 자동 갱신됩니다 (통합 15초 / KRX·NXT 10초)
                </div>
            )}
        </div>
    );
}
