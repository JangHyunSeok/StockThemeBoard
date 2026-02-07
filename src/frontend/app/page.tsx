'use client';

import { useVolumeRankByTheme } from '@/hooks/use-themes';
import ThemeSection from '@/components/ThemeSection';

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

    // 테마 목록 추출
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
            <div className="mb-4">
                <h1 className="text-2xl font-bold text-gray-900 mb-1">실시간 거래 상위 종목</h1>
                <p className="text-sm text-gray-600">테마별 거래대금 상위 종목 (실시간)</p>
            </div>

            {/* 모바일: 2열, 데스크톱: 3열 */}
            <div className="grid grid-cols-2 lg:grid-cols-3 gap-3">
                {themeNames.map((themeName) => (
                    <ThemeSection key={themeName} themeName={themeName} />
                ))}
            </div>

            <div className="mt-4 text-center text-xs text-gray-500">
                💡 거래대금 상위 종목이 자동으로 갱신됩니다 (60초)
            </div>
        </div>
    );
}
