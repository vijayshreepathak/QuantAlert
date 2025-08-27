import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database settings
    database_url: str = "sqlite:///./quantalert.db"
    duckdb_path: str = "./data/market_data.duckdb"
    
    # SMTP settings
    smtp_host: str = "localhost"
    smtp_port: int = 1025
    smtp_user: Optional[str] = None
    smtp_password: Optional[str] = None
    smtp_from: str = "alerts@quantalert.com"
    
    # API keys for market data providers
    openalgo_api_key: Optional[str] = None
    upstox_api_key: Optional[str] = None
    dhan_api_key: Optional[str] = None
    angel_api_key: Optional[str] = None
    angel_client_id: Optional[str] = None
    angel_password: Optional[str] = None
    angel_feed_token: Optional[str] = None
    alpha_vantage_api_key: Optional[str] = None
    
    # JWT settings
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Feed selection
    feed_provider: str = "auto"  # options: auto, simple, yahoo, alpha_vantage, angel, openalgo, upstox, dhan
    
    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
