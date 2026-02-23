import httpx
import json
from typing import Optional, Dict, Any
from datetime import datetime

from app.config import settings
from app.services.redis_client import get_cache, set_cache


class KISClient:
    """한국투자증권 OpenAPI 클라이언트"""
    
    TOKEN_CACHE_KEY = "kis:access_token"
    TOKEN_TTL = 86400  # 24시간
    
    def __init__(self):
        self.app_key = settings.KIS_APP_KEY
        self.app_secret = settings.KIS_APP_SECRET
        self.base_url = settings.KIS_BASE_URL
        self.account_number = settings.KIS_ACCOUNT_NUMBER
        
        # HTTP 클라이언트
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=30.0,
            headers={
                "Content-Type": "application/json; charset=utf-8"
            }
        )
    
    async def get_access_token(self) -> str:
        """액세스 토큰 발급 (캐시 우선)
        
        Returns:
            액세스 토큰 문자열
        """
        # Redis 캐시 확인
        cached_token = await get_cache(self.TOKEN_CACHE_KEY)
        if cached_token:
            return cached_token
        
        # 토큰 발급 API 호출
        url = "/oauth2/tokenP"
        body = {
            "grant_type": "client_credentials",
            "appkey": self.app_key,
            "appsecret": self.app_secret
        }
        
        response = await self.client.post(url, json=body)
        
        if response.status_code != 200:
            raise Exception(f"토큰 발급 실패: {response.text}")
        
        data = response.json()
        access_token = data.get("access_token")
        
        if not access_token:
            raise Exception("응답에 access_token이 없습니다")
        
        # Redis에 캐시 (24시간)
        await set_cache(self.TOKEN_CACHE_KEY, access_token, self.TOKEN_TTL)
        
        return access_token
    
    async def get_stock_quote(self, stock_code: str, market: str = "J") -> Dict[str, Any]:
        """실시간 주식 시세 조회
        
        Args:
            stock_code: 종목코드 (6자리)
            market: "J" (정규장 KRX) or "NX" (야간거래 NXT)
        
        Returns:
            시세 정보 딕셔너리
        """
        # 액세스 토큰 가져오기
        access_token = await self.get_access_token()
        
        # API 호출
        url = "/uapi/domestic-stock/v1/quotations/inquire-price"
        headers = {
            "authorization": f"Bearer {access_token}",
            "appkey": self.app_key,
            "appsecret": self.app_secret,
            "tr_id": "FHKST01010100"
        }
        params = {
            "fid_cond_mrkt_div_code": market,  # "J" (KRX) or "NX" (NXT)
            "fid_input_iscd": stock_code
        }
        
        response = await self.client.get(url, headers=headers, params=params)
        
        if response.status_code != 200:
            raise Exception(f"시세 조회 실패: {response.text}")
        
        data = response.json()
        
        # 에러 체크
        if data.get("rt_cd") != "0":
            error_msg = data.get("msg1", "알 수 없는 오류")
            raise Exception(f"API 오류: {error_msg}")
        
        output = data.get("output", {})
        
        # 응답 데이터 파싱
        # 참고: 종목명은 이 API에서 제공하지 않으므로 별도 조회 필요
        # Calculate Trading Value Change Rate manually
        curr_pr = int(output.get("stck_prpr", 0))
        curr_vol = int(output.get("acml_vol", 0))
        curr_tv = int(output.get("acml_tr_pbmn", 0))
        
        change_pr = int(output.get("prdy_vrss", 0))
        change_vol = int(output.get("prdy_vrss_vol", 0))
        
        prev_pr = curr_pr - change_pr
        prev_vol = curr_vol - change_vol
        prev_tv = prev_pr * prev_vol
        
        tv_change_rate = 0.0
        if prev_tv > 0:
            tv_change_rate = ((curr_tv - prev_tv) / prev_tv) * 100
        elif prev_tv <= 0 and curr_tv > 0:
            tv_change_rate = 100.0
            
        # 응답 데이터 파싱
        # 참고: 종목명은 이 API에서 제공하지 않으므로 별도 조회 필요
        return {
            "stock_code": stock_code,
            "stock_name": "",  # 종목명은 DB 또는 별도 API에서 조회
            "current_price": int(output.get("stck_prpr", 0)),      # 현재가
            "change_price": int(output.get("prdy_vrss", 0)),       # 전일대비 금액
            "change_rate": float(output.get("prdy_ctrt", 0)),      # 전일대비율
            "opening_price": int(output.get("stck_oprc", 0)),      # 시가
            "high_price": int(output.get("stck_hgpr", 0)),         # 고가
            "low_price": int(output.get("stck_lwpr", 0)),          # 저가
            "volume": int(output.get("acml_vol", 0)),              # 누적 거래량
            "trading_value": int(output.get("acml_tr_pbmn", 0)),   # 누적 거래대금
            "trading_value_change_rate": float(tv_change_rate),
            "sector": output.get("bstp_kor_isnm", "기타"),          # 업종 한글명
            "timestamp": datetime.now()
        }
    
    async def get_volume_rank(self, limit: int = 30, market: str = "J") -> list[Dict[str, Any]]:
        """거래량 순위 조회
        
        Args:
            limit: 조회할 종목 수 (최대 30, KIS API 제한)
            market: "J" (정규장 KRX) or "NX" (야간거래 NXT)
        
        Returns:
            거래량 순위 종목 리스트
        
        Note:
            KIS API는 최대 30건만 지원합니다.
            30건 초과 요청 시 자동으로 30건으로 조정됩니다.
        """
        # API 제한 체크
        if limit > 30:
            print(f"[WARNING] KIS 거래량순위 API는 최대 30건만 지원합니다. 요청: {limit}건 → 조정: 30건")
            limit = 30
        
        # 액세스 토큰 가져오기
        access_token = await self.get_access_token()
        
        # API 호출
        url = "/uapi/domestic-stock/v1/quotations/volume-rank"
        headers = {
            "authorization": f"Bearer {access_token}",
            "appkey": self.app_key,
            "appsecret": self.app_secret,
            "tr_id": "FHPST01710000"
        }
        params = {
            "fid_cond_mrkt_div_code": market,       # "J" (KRX) or "NX" (NXT)
            "fid_cond_scr_div_code": "20171",        # 거래대금 상위
            "fid_input_iscd": "0000",                # 전체 종목
            "fid_div_cls_code": "0",                 # 전체
            "fid_blng_cls_code": "0",                # 소속 구분 (전체)
            "fid_trgt_cls_code": "111111111",        # 대상 구분
            # 대상 제외 구분 (10자리)
            # 자리: 투자위험|투자경고|투자주의|관리종목|정리매매|불성실공시|ETF|ETN|신용불가|SPAC
            # 0=포함, 1=제외
            "fid_trgt_exls_cls_code": "0001111101", # 관리종목(4), 정리매매(5), 불성실공시(6), ETF(7), ETN(8), SPAC(10) 제외
            "fid_input_price_1": "",                 # 가격 조건 (미사용)
            "fid_input_price_2": "",                 # 가격 조건 (미사용)
            "fid_vol_cnt": "",                       # 거래량 조건 (미사용)
            "fid_input_date_1": "",                  # 날짜 조건 (미사용)
            "fid_input_cnt_1": str(limit),           # 조회 건수
            "fid_rank_sort_cls_code": "6"            # 정렬 기준: 6=거래대금 순 (0=상승률, 5=체결량)
        }
        
        # 요청 정보 로깅
        print(f"[DEBUG] KIS API Request:")
        print(f"[DEBUG]   URL: {url}")
        print(f"[DEBUG]   TR_ID: {headers['tr_id']}")
        print(f"[DEBUG]   Parameters:")
        for key, value in params.items():
            print(f"[DEBUG]     {key}: {value}")
        
        response = await self.client.get(url, headers=headers, params=params)
        
        print(f"[DEBUG] KIS API Response Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"[ERROR] HTTP Error: {response.status_code}")
            print(f"[ERROR] Response: {response.text}")
            raise Exception(f"거래량 순위 조회 실패: {response.text}")
        
        data = response.json()
        
        # 전체 응답 로깅 (디버깅용)
        print(f"[DEBUG] KIS API Response Keys: {list(data.keys())}")
        print(f"[DEBUG] rt_cd: {data.get('rt_cd')}")
        print(f"[DEBUG] msg_cd: {data.get('msg_cd')}")
        print(f"[DEBUG] msg1: {data.get('msg1')}")
        
        # 에러 체크
        if data.get("rt_cd") != "0":
            error_msg = data.get("msg1", "")
            msg_cd = data.get("msg_cd", "")
            rt_cd = data.get("rt_cd", "")
            
            # 전체 에러 정보 로깅
            print(f"[ERROR] KIS API Error Detected!")
            print(f"[ERROR]   rt_cd: {rt_cd}")
            print(f"[ERROR]   msg_cd: {msg_cd}")
            print(f"[ERROR]   msg1: {error_msg}")
            print(f"[ERROR] Full response: {data}")
            
            # 에러 메시지 구성
            if not error_msg:
                error_msg = f"알 수 없는 오류 (rt_cd: {rt_cd}, msg_cd: {msg_cd})"
            
            raise Exception(f"API 오류: {error_msg}")
        
        output = data.get("output", [])
        
        # 응답 데이터 파싱
        results = []
        for item in output:
            results.append({
                "code": item.get("mksc_shrn_iscd", ""),
                "name": item.get("hts_kor_isnm", ""),
                "rank": int(item.get("data_rank", 0)),
                "current_price": int(item.get("stck_prpr", 0)),
                "change_price": int(item.get("prdy_vrss", 0)),
                "change_rate": float(item.get("prdy_ctrt", 0)),
                "volume": int(item.get("acml_vol", 0)),
                "trading_value": int(item.get("acml_tr_pbmn", 0)),
            })
        
        return results
    
    async def close(self):
        """HTTP 클라이언트 종료"""
        await self.client.aclose()


# 싱글톤 인스턴스
_kis_client: Optional[KISClient] = None


async def get_kis_client() -> KISClient:
    """KIS 클라이언트 가져오기 (싱글톤)"""
    global _kis_client
    if _kis_client is None:
        _kis_client = KISClient()
    return _kis_client
