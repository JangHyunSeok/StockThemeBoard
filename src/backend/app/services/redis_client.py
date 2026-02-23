import redis.asyncio as redis
from typing import Optional
from app.config import settings


# Redis 클라이언트 인스턴스 (싱글톤)
_redis_client: Optional[redis.Redis] = None


async def get_redis_client() -> redis.Redis:
    """Redis 클라이언트 가져오기 (싱글톤)"""
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )
    return _redis_client


async def get_cache(key: str) -> Optional[str]:
    """Redis에서 캐시 조회"""
    client = await get_redis_client()
    return await client.get(key)


async def set_cache(key: str, value: str, ttl: int = 60) -> None:
    """Redis에 캐시 저장
    
    Args:
        key: 캐시 키
        value: 캐시 값
        ttl: 유효기간 (초), 기본 60초
    """
    try:
        client = await get_redis_client()
        await client.setex(key, ttl, value)
    except Exception as e:
        # Redis 에러 시 로깅만 하고 계속 진행
        print(f"[WARNING] Redis cache write failed: {type(e).__name__}: {str(e)}")


async def delete_cache(key: str) -> None:
    """Redis에서 캐시 삭제"""
    client = await get_redis_client()
    await client.delete(key)


async def close_redis():
    """Redis 연결 종료"""
    global _redis_client
    if _redis_client:
        await _redis_client.close()
        _redis_client = None
