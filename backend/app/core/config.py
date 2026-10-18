from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str = "MeetSpot"
    APP_ENV: str = "production"
    DEBUG: bool = False
    APP_URL: str = "https://meet.oussamma.tn"
    BACKEND_URL: str = "https://meet.oussamma.tn"
    FRONTEND_URL: str = "https://meet.oussamma.tn"
    
    SECRET_KEY: str = "super_secret_jwt_key_meetspot_2026_dev_prod"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://meetspot_user:meetspot_secure_password_2026@localhost:5432/meetspot_db"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # SSO Ecosystem
    SSO_BASE_URL: str = "https://sso-a.oussamma.tn"
    SSO_CLIENT_ID: str = "client_meetspot_app"
    SSO_CLIENT_SECRET: str = "sec_meetspot_platform_secret_2026"
    SSO_REDIRECT_URI: str = "https://meet.oussamma.tn/auth/callback"
    SSO_SCOPES: str = "openid profile email"
    SUPER_ADMIN_EMAILS: str = "contact@oussamma.tn"
    
    # LiteLLM Gateway
    LITELLM_BASE_URL: str = "https://ai.oussamma.tn/v1"
    LITELLM_API_KEY: str = "sk-oussamma-master-gateway-2026"
    LITELLM_DEFAULT_MODEL: str = "chatgpt/gpt-5.4"
    
    # Routing & Maps
    ROUTING_PROVIDER: str = "mock"  # mock | ors | valhalla | osrm
    ORS_API_KEY: Optional[str] = None
    NOMINATIM_BASE_URL: str = "https://nominatim.openstreetmap.org"
    
    CORS_ORIGINS: List[str] = [
        "https://meet.oussamma.tn",
        "https://oussamma.tn",
        "http://localhost:3000",
        "http://localhost:8000"
    ]

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
