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
        
        # 개장일 여부 확인 (주말 + 공휴일 체크)
        # 20시 이후에는 모든 관점(KRX, NXT)에서 장이 종료된 것으로 간주하여 DB 조회 모드로 전환
        now = datetime.now()
        market_open = is_market_open() and (9 <= now.hour < 20)
        print(f"[DEBUG] Market open status (Time-aware): {market_open}")
        
        if market_open:
            # 개장일: KIS API 조회
            print(f"[DEBUG] Fetching from KIS API (market open)")
            kis_client = await get_kis_client()
            
            # market 파라미터에 따라 API 호출
            # KRX="J", NXT="NX", ALL=KRX+NXT 별도 조회 후 병합 (UN 코드 미지원)
            if market == "ALL":
                krx_ranks = await kis_client.get_volume_rank(limit=30, market="J")
                nxt_ranks = await kis_client.get_volume_rank(limit=30, market="NX")
                
                # 병합 맵 생성
                merged_map = {}
                
                # 1. KRX 데이터 먼저 투입
                for r in krx_ranks:
                    merged_map[r["code"]] = r.copy()
                    
                # 2. NXT 데이터 병합 (합산 및 덮어쓰기)
                for r in nxt_ranks:
                    code = r["code"]
                    if code in merged_map:
                        # 동일 종목 존재: 거래대금 합산 및 NXT 시세 우선
                        merged_map[code]["trading_value"] += r["trading_value"]
                        merged_map[code]["current_price"] = r["current_price"]
                        merged_map[code]["change_price"] = r["change_price"]
                        merged_map[code]["change_rate"] = r["change_rate"]
                        merged_map[code]["volume"] += r["volume"]  # 거래량도 합산
                    else:
                        merged_map[code] = r.copy()
                
                # 3. 거래대금 순 정렬 후 상위 30개
                rankings = sorted(merged_map.values(), key=lambda x: x["trading_value"], reverse=True)[:30]
            else:
                api_market_code = {"NXT": "NX"}.get(market, "J")
                rankings = await kis_client.get_volume_rank(limit=30, market=api_market_code)
            print(f"[DEBUG] KIS API returned {len(rankings)} rankings")
            
            # 15:30 이후면 KRX DB에 저장, 20:00 이후면 NXT DB에 저장
            now = datetime.now()
            if market == "KRX" and (now.hour > 15 or (now.hour == 15 and now.minute >= 30)):
                today = now.date()
                await crud_daily_ranking.save_daily_rankings(db, today, rankings, market_type="KRX")
            elif market == "NXT" and now.hour >= 20:
                today = now.date()
                await crud_daily_ranking.save_daily_rankings(db, today, rankings, market_type="NXT")
        else:
            # 휴장일: 가장 최근 개장일 DB 조회
            # DB에서는 종목코드, 종목명, 랭크, market_type만 사용
            # 가격/등락률/거래량 등은 실시간 조회로 업데이트
            last_market_date = get_last_market_date()
            print(f"[DEBUG] Market closed. Fetching from DB for date: {last_market_date}")

            if market == "ALL":
                # 통합시세: KRX + NXT DB 데이터 병합 후 거래대금 상위 30개
                krx = await crud_daily_ranking.get_rankings_by_date(db, last_market_date, market_type="KRX")
                nxt = await crud_daily_ranking.get_rankings_by_date(db, last_market_date, market_type="NXT")
                seen = set()
                merged = []
                for r in sorted((krx or []) + (nxt or []), key=lambda x: x.get("trading_value", 0), reverse=True):
                    if r["code"] not in seen:
                        seen.add(r["code"])
                        merged.append(r)
                rankings = merged[:30]
            else:
                rankings = await crud_daily_ranking.get_rankings_by_date(db, last_market_date, market_type=market)
            print(f"[DEBUG] DB returned {len(rankings) if rankings else 0} rankings")
            
            if not rankings:
                print(f"[WARN] No rankings found in DB for date {last_market_date}, market {market}")
                rankings = []
            
            # 실시간 시세 업데이트 (병렬 처리)
            # 평일이므로 실시간 시세 업데이트 진행
            if rankings:
                try:
                    print(f"[DEBUG] Starting real-time quote updates for {len(rankings)} stocks")
                    kis_client = await get_kis_client()
                    
                    # 토큰 미리 확보 (Concurrency Issue 방지)
                    await kis_client.get_access_token()
                    print(f"[DEBUG] KIS token acquired")
                    
                    # market 파라미터 설정 (KRX/NXT 구분)
                    # ALL인 경우 NXT 실시간 시세를 우선적으로 시도
                    api_market_code = "NX" if market in ("NXT", "ALL") else "J"
                    
                    # 업데이트 함수 정의
                    async def update_quote(ranking):
                        try:
                            # 1차 시도 (NXT if ALL/NXT, else KRX)
                            quote = await kis_client.get_stock_quote(ranking['code'], market=api_market_code)
                            
                            # 순위는 유지하되, 가격/거래량 정보는 실시간 데이터로 덮어쓰기
                            ranking['current_price'] = quote['current_price']
                            ranking['change_price'] = quote['change_price']
                            ranking['change_rate'] = quote['change_rate']
                            ranking['volume'] = quote['volume']
                            ranking['trading_value'] = quote.get('trading_value', 0)
                            ranking['trading_value_change_rate'] = quote.get('trading_value_change_rate')
                            
                        except Exception as e:
                            # 2차 시도: ALL 모드에서 NXT 실패 시 KRX fallback
                            if market == "ALL" and api_market_code == "NX":
                                try:
                                    print(f"[DEBUG] NXT fallback to KRX for {ranking.get('name', '')}")
                                    quote = await kis_client.get_stock_quote(ranking['code'], market="J")
                                    ranking['current_price'] = quote['current_price']
                                    ranking['change_price'] = quote['change_price']
                                    ranking['change_rate'] = quote['change_rate']
                                    ranking['volume'] = quote['volume']
                                    ranking['trading_value'] = quote.get('trading_value', 0)
                                    ranking['trading_value_change_rate'] = quote.get('trading_value_change_rate')
                                except Exception as e2:
                                    print(f"[WARN] Quote update failed for {ranking.get('name', '')} (NXT & KRX): {str(e2)}")
                            else:
                                print(f"[WARN] Quote update failed for {ranking.get('name', '')}: {str(e)}")

                    # 청크 단위 병렬 실행 (Rate Limit 고려)
                    CHUNK_SIZE = 20
                    for i in range(0, len(rankings), CHUNK_SIZE):
                        chunk = rankings[i:i + CHUNK_SIZE]
                        await asyncio.gather(*[update_quote(r) for r in chunk])
                        await asyncio.sleep(0.05)
                    
                    print(f"[DEBUG] Real-time quote updates completed")
                    
                except Exception as e:
                    print(f"[ERROR] Real-time quote update process failed: {str(e)}")
                    import traceback
                    traceback.print_exc()
        
        # 업종별 동적 분류 및 정렬 (KIS API 실시간 업종명 + Redis 24h 캐시)
        print(f"[DEBUG] Classifying {len(rankings)} stocks by sector")
        kis_client = await get_kis_client()
        api_market_code = "NX" if market == "NXT" else "J"
        sector_map = await get_sector_map_from_cache_or_api(rankings, kis_client, api_market_code)
        result = classify_by_sector(rankings, sector_map)
        print(f"[DEBUG] Classification complete - {len(result)} sectors")
        
        # 캐시 저장 (장중 3초, 장후 1시간)
        is_after_hours = now.hour >= 20 or now.hour < 9
        ttl = 3600 if is_after_hours else 3
        await set_cache(cache_key, json.dumps(result, ensure_ascii=False), ttl=ttl)
        
        return result
    
    except Exception as e:
        error_msg = f"거래량 순위 조회 실패: {type(e).__name__}: {str(e)}"
        print(f"[ERROR] {error_msg}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=error_msg
        )
