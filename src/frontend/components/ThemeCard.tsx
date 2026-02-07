import Link from 'next/link';
import { Theme } from '@/types';

interface ThemeCardProps {
    theme: Theme;
}

export default function ThemeCard({ theme }: ThemeCardProps) {
    return (
        <Link href={`/themes/${theme.id}`}>
            <div className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-lg transition-shadow cursor-pointer">
                <h3 className="text-xl font-bold text-gray-900 mb-2">
                    {theme.name}
                </h3>
                <p className="text-gray-600 text-sm line-clamp-2">
                    {theme.description}
                </p>
                <div className="mt-4 flex items-center text-sm text-blue-600">
                    <span>상세 보기</span>
                    <svg className="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                    </svg>
                </div>
            </div>
        </Link>
    );
}
