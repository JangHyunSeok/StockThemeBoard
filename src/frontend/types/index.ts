// 테마 타입
export interface Theme {
    id: string;
    name: string;
    description: string;
    created_at: string;
    updated_at: string;
}

// 종목 타입 (테마 내)
export interface StockInTheme {
    code: string;
    name: string;
    market: string;
    weight: number;
}

// 테마 상세 (종목 포함)
export interface ThemeDetail extends Theme {
    stocks: StockInTheme[];
}

// 실시간 시세
export interface StockQuote {
    stock_code: string;
    stock_name: string;
    current_price: number;
    change_price: number;
    change_rate: number;
    opening_price: number;
    high_price: number;
    low_price: number;
    volume: number;
    timestamp: string;
}

// 거래량 순위 (실시간 API)
export interface StockRanking {
    code: string;
    name: string;
    rank: number;
    current_price: number;
    change_price: number;
    change_rate: number;
    volume: number;
    trading_value: number;
    trading_value_change_rate?: number; // 전일대비 증가율 (Volume Increase Rate as proxy)
}

// 지수 시세
export interface IndexQuote {
    index_code: string;
    current_price: number;
    change_price: number;
    change_rate: number;
    timestamp: string;
}

export interface IndicesResponse {
    items: IndexQuote[];
}
