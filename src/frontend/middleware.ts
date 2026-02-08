import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(request: NextRequest) {
    if (request.nextUrl.pathname.startsWith('/api')) {
        console.log('----------------------------------------')
        console.log('📌 [Middleware] API 요청 수신:', request.nextUrl.pathname)
        console.log('   Host:', request.headers.get('host'))
        console.log('   User-Agent:', request.headers.get('user-agent'))
        console.log('----------------------------------------')
    }
}

export const config = {
    matcher: '/api/:path*',
}
