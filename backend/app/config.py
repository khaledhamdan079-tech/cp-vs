from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    database_url: str
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440
    codeforces_api_url: str = "https://codeforces.com/api"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Read environment variables directly (Railway uses uppercase)
# This ensures Railway's uppercase env vars are properly mapped
_env_vars = {}
if 'DATABASE_URL' in os.environ:
    _env_vars['database_url'] = os.environ['DATABASE_URL']
if 'JWT_SECRET_KEY' in os.environ:
    _env_vars['jwt_secret_key'] = os.environ['JWT_SECRET_KEY']
if 'JWT_ALGORITHM' in os.environ:
    _env_vars['jwt_algorithm'] = os.environ['JWT_ALGORITHM']
if 'ACCESS_TOKEN_EXPIRE_MINUTES' in os.environ:
    _env_vars['access_token_expire_minutes'] = int(os.environ['ACCESS_TOKEN_EXPIRE_MINUTES'])
if 'CODEFORCES_API_URL' in os.environ:
    _env_vars['codeforces_api_url'] = os.environ['CODEFORCES_API_URL']

# Also check lowercase versions (for local .env file)
if 'database_url' in os.environ and 'database_url' not in _env_vars:
    _env_vars['database_url'] = os.environ['database_url']
if 'jwt_secret_key' in os.environ and 'jwt_secret_key' not in _env_vars:
    _env_vars['jwt_secret_key'] = os.environ['jwt_secret_key']

# Create settings with environment variables
# If _env_vars is empty, Settings() will read from .env file or raise error
settings = Settings(**_env_vars) if _env_vars else Settings()
