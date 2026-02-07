from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """애플리케이션 설정"""
    
    # 한국투자증권 API 설정
    KIS_APP_KEY: str = ""
    KIS_APP_SECRET: str = ""
    KIS_ACCOUNT_NUMBER: str = ""
    KIS_BASE_URL: str = "https://openapi.koreainvestment.com:9443"
    
    # 데이터베이스 설정
    DATABASE_URL: str = "postgresql+asyncpg://stockuser:stockpass@localhost:5432/stocktheme"
    
    # Redis 설정
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # 서버 환경
    ENVIRONMENT: str = "development"
    
    # JWT Secret Key (향후 사용자 인증 기능 추가 시 사용)
    # 현재 버전에서는 사용하지 않음 - 공개 접근 앱
    SECRET_KEY: str = "change-this-secret-key"
    
    # CORS 설정 (콤마로 구분된 문자열)
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:8000"
    
    def get_allowed_origins(self) -> list[str]:
        """ALLOWED_ORIGINS 문자열을 리스트로 변환"""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
