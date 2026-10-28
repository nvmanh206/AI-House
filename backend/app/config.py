from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import model_validator, Field

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')
    database_url: str = 'postgresql+psycopg://utility:utility@localhost:5432/utility'
    jwt_secret: str = ''
    jwt_algorithm: str = 'HS256'
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    refresh_cookie_name: str = Field(default='utility_refresh', pattern=r'^[A-Za-z0-9_-]+$')
    llm_provider: str = 'deterministic'
    llm_api_key: str = ''
    gemini_api_key: str = ''
    gemini_model: str = 'gemini-3.5-flash-lite'
    gemini_search_enabled: bool = True
    gemini_timeout_seconds: int = Field(default=25, ge=5, le=120)
    gemini_reply_tokens: int = Field(default=2048,ge=512,le=8192)
    gemini_quota_guard_enabled: bool = False
    gemini_requests_per_minute: int = Field(default=12,ge=1,le=100)
    knowledge_rag_enabled: bool = False
    knowledge_database_url: str = ''
    knowledge_embedding_model: str = 'gemini-embedding-2'
    knowledge_archive_path: str = '../.local/knowledge'
    app_env: str = 'development'
    bootstrap_first_user_admin: bool = False
    frontend_url: str = 'http://localhost:3000'
    rate_limit_enabled: bool = True
    rate_limit_auth_per_min: int = 30
    rate_limit_refresh_per_min: int = 120
    @model_validator(mode='after')
    def check_secret(self):
        if len(self.jwt_secret) < 32:
            raise ValueError('JWT_SECRET must contain at least 32 characters; configure .env')
        if self.jwt_algorithm != 'HS256':
            raise ValueError('Only HS256 is supported in V1')
        return self

settings = Settings()
