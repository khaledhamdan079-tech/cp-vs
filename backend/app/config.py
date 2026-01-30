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

# Check for DATABASE_URL (Railway's standard name, also check alternatives)
database_url = None
for var_name in ['DATABASE_URL', 'POSTGRES_URL', 'PGDATABASE', 'POSTGRESQL_URL']:
    if var_name in os.environ:
        database_url = os.environ[var_name]
        break
# Also check lowercase (for local .env file)
if not database_url and 'database_url' in os.environ:
    database_url = os.environ['database_url']

if database_url:
    _env_vars['database_url'] = database_url

# Read other environment variables
if 'JWT_SECRET_KEY' in os.environ:
    _env_vars['jwt_secret_key'] = os.environ['JWT_SECRET_KEY']
elif 'jwt_secret_key' in os.environ:
    _env_vars['jwt_secret_key'] = os.environ['jwt_secret_key']

if 'JWT_ALGORITHM' in os.environ:
    _env_vars['jwt_algorithm'] = os.environ['JWT_ALGORITHM']
elif 'jwt_algorithm' in os.environ:
    _env_vars['jwt_algorithm'] = os.environ['jwt_algorithm']

if 'ACCESS_TOKEN_EXPIRE_MINUTES' in os.environ:
    _env_vars['access_token_expire_minutes'] = int(os.environ['ACCESS_TOKEN_EXPIRE_MINUTES'])
elif 'access_token_expire_minutes' in os.environ:
    _env_vars['access_token_expire_minutes'] = int(os.environ['access_token_expire_minutes'])

if 'CODEFORCES_API_URL' in os.environ:
    _env_vars['codeforces_api_url'] = os.environ['CODEFORCES_API_URL']
elif 'codeforces_api_url' in os.environ:
    _env_vars['codeforces_api_url'] = os.environ['codeforces_api_url']

# Create settings with environment variables
# If _env_vars is empty, Settings() will read from .env file or raise error
# Check if we're missing DATABASE_URL and provide helpful error
if not database_url and not any('database' in k.lower() for k in os.environ.keys()):
    # Check if we're likely on Railway (has PORT or RAILWAY env vars)
    is_railway = 'PORT' in os.environ or 'RAILWAY_ENVIRONMENT' in os.environ
    if is_railway:
        raise ValueError(
            "DATABASE_URL is required but not found. "
            "On Railway, you need to add a PostgreSQL database service:\n"
            "1. Go to your Railway project\n"
            "2. Click 'New' → 'Database' → 'Add PostgreSQL'\n"
            "3. Railway will automatically set DATABASE_URL\n"
            "4. Redeploy your backend service"
        )
    else:
        raise ValueError(
            "DATABASE_URL environment variable is required. "
            "Set it in your .env file or environment variables."
        )

settings = Settings(**_env_vars) if _env_vars else Settings()
