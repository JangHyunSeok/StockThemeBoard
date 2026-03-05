from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List, Dict, Optional
from collections import OrderedDict
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, date, timedelta
import asyncio
import json

from app.services.kis_client import get_kis_client
from app.services.redis_client import get_cache, set_cache
from app.schemas.stock_ranking import StockRanking
from app.crud import daily_ranking as crud_daily_ranking
from app.database import get_db
from app.core.utils import is_market_open, get_last_market_date, get_current_market_type
from app.core.themes import SECTOR_OVERRIDE_MAP


router = APIRouter()


def is_weekend() -> bool:
    """주말 여부 확인 (간단 버전)"""
    today = datetime.now()
    return today.weekday() >= 5  # 5=토요일, 6=일요일


def is_after_market_close() -> bool:
    """장 마감 시간(15:30) 이후 확인"""
    now = datetime.now()
    return now.hour > 15 or (now.hour == 15 and now.minute >= 30)


def get_last_weekday() -> date:
    """마지막 평일 날짜 조회"""
    today = datetime.now().date()
    current = today
    
    # 최대 7일 전까지 검색
    for _ in range(7):
        dt = datetime.combine(current, datetime.min.time())
        if dt.weekday() < 5:  # 평일
            return current
        current -= timedelta(days=1)
    
    return today


# ──────────────────────────────────────────────────────────────────────────────
# 종목코드 → 업종명 매핑은 KIS API(bstp_kor_isnm)에서 실시간으로 조회
# Redis에 24시간 캐시하여 성능 보장
# ──────────────────────────────────────────────────────────────────────────────
SECTOR_MAP_CACHE_PREFIX = "sector_map:"
SECTOR_MAP_CACHE_TTL = 86400  # 24시간


async def get_sector_map_from_cache_or_api(
    rankings: List[Dict],
    kis_client,
    market_code: str
) -> Dict[str, str]:
    """
    종목코드 → 업종명 매핑 반환
    우선순위:
      1. SECTOR_OVERRIDE_MAP (항상 최우선 — 캐시/API 무관)
      2. Redis 캐시 (24h TTL)
      3. KIS get_stock_quote() API 호출
    """
    result: Dict[str, str] = {}
    miss_codes: List[str] = []

    for stock in rankings:
        code = stock["code"]
        # 1순위: 오버라이드 맵 (캐시보다 항상 우선)
        if code in SECTOR_OVERRIDE_MAP:
            result[code] = SECTOR_OVERRIDE_MAP[code]
            continue
        # 2순위: Redis 캐시
        cached = await get_cache(f"{SECTOR_MAP_CACHE_PREFIX}{code}")
        if cached:
            result[code] = cached
        else:
            miss_codes.append(code)

    if miss_codes:
        print(f"[DEBUG] Sector cache miss for {len(miss_codes)} stocks: {miss_codes}")

        async def fetch_sector(code: str):
            try:
                quote = await kis_client.get_stock_quote(code, market=market_code)
                # KIS API 업종명 (오버라이드 맵에 없는 종목만 여기 도달)
                sector = quote.get("sector") or "기타"
                await set_cache(
                    f"{SECTOR_MAP_CACHE_PREFIX}{code}",
                    sector,
                    ttl=SECTOR_MAP_CACHE_TTL
                )
                return code, sector
            except Exception as e:
                print(f"[WARN] Sector fetch failed for {code}: {e}")
                return code, "기타"

        fetched = await asyncio.gather(*[fetch_sector(c) for c in miss_codes])
        result.update(dict(fetched))
    else:
        print(f"[DEBUG] All sector mappings resolved (override or cache)")

    return result


def classify_by_sector(rankings: List[Dict], sector_map: Dict[str, str]) -> Dict[str, List[Dict]]:
    """
    업종별 분류 및 거래대금 순 정렬
    - sector_map: { 종목코드: 업종명 } (KIS API에서 조회한 실시간 데이터)
    - 매핑 없는 종목은 '기타' 섹터로 분류, 맨 마지막에 표시
    """
    sector_stocks: Dict[str, List[Dict]] = {}

    for stock_data in rankings:
        sector = sector_map.get(stock_data["code"], "기타")
        if sector not in sector_stocks:
            sector_stocks[sector] = []
        sector_stocks[sector].append(stock_data)

    # '기타' 섹터는 별도 보관 후 맨 마지막에 추가
    other_stocks = sector_stocks.pop("기타", [])

    # 각 섹터의 총 거래대금 계산 → 거래대금 순 정렬
    sector_totals = {
        name: sum(s["trading_value"] for s in stocks)
        for name, stocks in sector_stocks.items()
    }
    sorted_sectors = sorted(sector_totals.items(), key=lambda x: x[1], reverse=True)

    print("[DEBUG] Sector totals (sorted):")
    for name, total in sorted_sectors:
        print(f"  {name}: {total:,}")

    result = OrderedDict()
    for sector_name, _ in sorted_sectors:
        sorted_stocks = sorted(sector_stocks[sector_name], key=lambda x: x["trading_value"], reverse=True)
        result[sector_name] = [StockRanking(**s).model_dump() for s in sorted_stocks]

    # '기타' 섹터는 맨 마지막에 추가
    if other_stocks:
        sorted_other = sorted(other_stocks, key=lambda x: x["trading_value"], reverse=True)
        result["기타"] = [StockRanking(**s).model_dump() for s in sorted_other]

    print(f"[DEBUG] Result key order: {list(result.keys())}")
    return result


# 기존 import는 위에서 처리됨

@router.get("/volume-rank-by-theme")
async def get_volume_rank_by_theme(
    market: Optional[str] = Query(None, description="Market type: KRX, NXT, ALL(통합시세). Auto-detect if not specified."),
    db: AsyncSession = Depends(get_db)
):
    """테마별 거래량 상위 종목 조회 (영업일/휴일 대응, KRX/NXT/ALL 지원)"""
    
    # 1. market 파라미터가 없으면 시간대별 자동 결정
    if market is None:
        market = get_current_market_type()  # "KRX" or "NXT"
    
    print(f"[DEBUG] Request received - market: {market}, current time: {datetime.now()}")
    
    # 2. 캐시 키에 market 포함
    cache_key = f"volume_rank_by_theme:{market}"
    cached_data = await get_cache(cache_key)
    
    if cached_data:
        print(f"[DEBUG] Returning cached data")
        return json.loads(cached_data)
    
    try:
        rankings = []
        now = datetime.now()
        is_open_day = is_market_open()
        time_val = now.hour * 100 + now.minute
        
        krx_source = "DB"
        nxt_source = "DB"
        
        # 1. 각 마켓별 데이터 소스 결정 (유저 요구사항 1~5 만족)
        if is_open_day:
            if 800 <= time_val < 900:
                krx_source = "NONE"   # 1. 08:00 ~ 09:00: NXT 기준 데이터만 조회 (KRX 필요없음)
                nxt_source = "LIVE"
            elif 900 <= time_val < 1540:
                krx_source = "LIVE"   # 2. 09:00 ~ 15:40: KRX + NXT 데이터 실시간
                nxt_source = "LIVE"
            elif 1540 <= time_val < 2000:
                krx_source = "DB"     # 3. 15:40 ~ 20:00: 15:40 스케줄러(DB) + NXT 실시간
                nxt_source = "LIVE"
            else:
                krx_source = "DB"     # 4. 20:00 ~ 23:59:59 (및 00:00 ~ 08:00): 둘 다 DB
                nxt_source = "DB"
        else:
            krx_source = "DB"         # 5. 주말 및 공휴일: 직전 영업일 디비
            nxt_source = "DB"
            
        print(f"[DEBUG] Rules applied - KRX Source: {krx_source}, NXT Source: {nxt_source}")

        kis_client = await get_kis_client()
        last_date = get_last_market_date()

        async def fetch_source(market_type, source, limit=30):
            """정해진 source 규칙에 따라 리스트를 가져옵니다."""
            if source == "NONE":
                return []
            elif source == "LIVE":
                api_code = "J" if market_type == "KRX" else "NX"
                try:
                    # 토큰 미리 확보
                    await kis_client.get_access_token()
                    return await kis_client.get_volume_rank(limit=limit, market=api_code)
                except Exception as e:
                    print(f"[WARN] Failed to fetch {market_type} LIVE data: {e}")
                    return []
            else: # "DB"
                try:
                    db_ranks = await crud_daily_ranking.get_rankings_by_date(db, last_date, market_type=market_type)
                    return db_ranks[:limit] if db_ranks else []
                except Exception as e:
                    print(f"[WARN] Failed to fetch {market_type} DB data: {e}")
                    return []

        # 마켓에 따른 병합 처리
        if market == "ALL":
            krx_ranks = await fetch_source("KRX", krx_source)
            nxt_ranks = await fetch_source("NXT", nxt_source)
            
            merged_map = {}
            for r in krx_ranks:
                merged_map[r["code"]] = r.copy()
            
            for r in nxt_ranks:
                code = r["code"]
                if code in merged_map:
                    merged_map[code]["trading_value"] += r.get("trading_value", 0)
                    merged_map[code]["volume"] += r.get("volume", 0)
                    # 통합시세에서는 최신값(주로 NXT 혹은 최근 DB값)을 현재가로 표시
                    merged_map[code]["current_price"] = r.get("current_price", 0)
                    merged_map[code]["change_price"] = r.get("change_price", 0)
                    merged_map[code]["change_rate"] = r.get("change_rate", 0)
                else:
                    merged_map[code] = r.copy()
                    
            # 09:00 ~ 15:40 둘 다 실시간일 경우에만 KRX 데이터 누락분 보충
            if krx_source == "LIVE" and nxt_source == "LIVE":
                krx_codes = {r["code"] for r in krx_ranks}
                missing_krx_codes = [r["code"] for r in nxt_ranks if r["code"] not in krx_codes]
                if missing_krx_codes:
                    extra_results = await asyncio.gather(*[
                        kis_client.get_stock_quote(code, market="J")
                        for code in missing_krx_codes
                    ], return_exceptions=True)
                    for code, res in zip(missing_krx_codes, extra_results):
                        if isinstance(res, dict) and code in merged_map:
                            merged_map[code]["trading_value"] += res.get("trading_value", 0)
                            merged_map[code]["volume"] += res.get("volume", 0)
            
            rankings = sorted(merged_map.values(), key=lambda x: x.get("trading_value", 0), reverse=True)[:30]
        else:
            # 단일 마켓일 경우
            target_source = krx_source if market == "KRX" else nxt_source
            rankings = await fetch_source(market, target_source)
        
        # 업종별 동적 분류 및 정렬 (KIS API 실시간 업종명 + Redis 24h 캐시)
        print(f"[DEBUG] Classifying {len(rankings)} stocks by sector")
        kis_client = await get_kis_client()
        api_market_code = "NX" if market == "NXT" else "J"
        sector_map = await get_sector_map_from_cache_or_api(rankings, kis_client, api_market_code)
        result = classify_by_sector(rankings, sector_map)
        print(f"[DEBUG] Classification complete - {len(result)} sectors")
        
        # 캐시 저장 (마켓별 TTL 조정)
        # - ALL(통합시세): KRX + NXT + 개별조회로 3~4초 소요 → TTL 15초
        # - KRX/NXT: 단일 조회로 1~2초 소요 → TTL 10초
        # - 장 외: 1시간
        if krx_source == "DB" and nxt_source == "DB":
            ttl = 3600
        elif market == "ALL":
            ttl = 15  # KIS 3회 호출 소요시간 감안
        else:
            ttl = 10  # KIS 1회 호출 소요시간 감안
        await set_cache(cache_key, json.dumps(result, ensure_ascii=False), ttl=ttl)
        
        return result
    
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        error_msg = f"거래량 순위 조회 실패: {type(e).__name__}: {str(e)}\n\n{tb}"
        print(f"[ERROR] {error_msg}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=error_msg
        )
