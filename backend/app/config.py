from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # Railway provides DATABASE_URL (uppercase), Pydantic will map it automatically
    database_url: str
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440
    codeforces_api_url: str = "https://codeforces.com/api"
    
    class Config:
        env_file = ".env"
        # Pydantic Settings automatically maps DATABASE_URL to database_url
        # But we'll also check uppercase versions explicitly
        case_sensitive = False
        
    def __init__(self, **kwargs):
        # Explicitly handle Railway's uppercase environment variables
        # Railway provides: DATABASE_URL, JWT_SECRET_KEY, etc.
        env_mapping = {
            'DATABASE_URL': 'database_url',
            'JWT_SECRET_KEY': 'jwt_secret_key',
            'JWT_ALGORITHM': 'jwt_algorithm',
            'ACCESS_TOKEN_EXPIRE_MINUTES': 'access_token_expire_minutes',
            'CODEFORCES_API_URL': 'codeforces_api_url',
        }
        
        # Map uppercase env vars to lowercase field names
        for env_key, field_name in env_mapping.items():
            if field_name not in kwargs and env_key in os.environ:
                value = os.environ[env_key]
                # Convert ACCESS_TOKEN_EXPIRE_MINUTES to int
                if field_name == 'access_token_expire_minutes':
                    value = int(value)
                kwargs[field_name] = value
        
        super().__init__(**kwargs)


settings = Settings()
