from fastapi import APIRouter, HTTPException
from typing import List
import json
from app.services.kis_client import get_kis_client
from app.services.redis_client import get_cache, set_cache
from app.schemas.index import IndexQuote, IndicesResponse

router = APIRouter()

INDICES_CACHE_KEY = "indices:current"
INDICES_CACHE_TTL = 30  # 30초 캐시 (폴링 시 불필요한 KIS API 반복 호출 방지)

@router.get("/current", response_model=IndicesResponse, summary="주요 지수 시세 조회")
async def get_current_indices():
    """
    코스피(0001)와 코스닥(1001)의 현재 지수 시세를 조회합니다.
    """
    # Redis 캐시 확인 (30초)
    cached = await get_cache(INDICES_CACHE_KEY)
    if cached:
        return IndicesResponse(**json.loads(cached))

    try:
        kis_client = await get_kis_client()
        # 토큰 1회 선발급 후 코스피 / 코스닥 2회 호출에 공유
        access_token = await kis_client.get_access_token()

        kospi  = await kis_client.get_index_quote("0001", access_token=access_token)
        kosdaq = await kis_client.get_index_quote("1001", access_token=access_token)

        result = IndicesResponse(items=[
            IndexQuote(**kospi),
            IndexQuote(**kosdaq)
        ])

        # 결과 캐시 저장 (30초)
        await set_cache(INDICES_CACHE_KEY, result.model_dump_json(), ttl=INDICES_CACHE_TTL)

        return result

    except Exception as e:
        import traceback
        print(f"❌ 지수 조회 중 오류 발생: {str(e)}")
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"지수 정보를 가져오는 중 오류가 발생했습니다: {str(e)}"
        )
