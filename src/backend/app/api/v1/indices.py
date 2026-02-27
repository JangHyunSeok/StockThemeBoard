from fastapi import APIRouter, HTTPException
from typing import List
from app.services.kis_client import get_kis_client
from app.schemas.index import IndexQuote, IndicesResponse

router = APIRouter()

@router.get("/current", response_model=IndicesResponse, summary="주요 지수 시세 조회")
async def get_current_indices():
    """
    코스피(0001)와 코스닥(1001)의 현재 지수 시세를 조회합니다.
    """
    try:
        kis_client = await get_kis_client()
        
        # 코스피와 코스닥 지수 조회
        kospi = await kis_client.get_index_quote("0001")
        kosdaq = await kis_client.get_index_quote("1001")
        
        return IndicesResponse(items=[
            IndexQuote(**kospi),
            IndexQuote(**kosdaq)
        ])
    except Exception as e:
        import traceback
        print(f"❌ 지수 조회 중 오류 발생: {str(e)}")
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"지수 정보를 가져오는 중 오류가 발생했습니다: {str(e)}"
        )
