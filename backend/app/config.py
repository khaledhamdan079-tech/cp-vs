from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    database_url: str
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440
    codeforces_api_url: str = "https://codeforces.com/api"
    
    class Config:
        env_file = ".env"


settings = Settings()
