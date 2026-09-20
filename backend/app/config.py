from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import model_validator

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')
    database_url: str = 'postgresql+psycopg://utility:utility@localhost:5432/utility'
    jwt_secret: str = ''
    jwt_algorithm: str = 'HS256'
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    llm_provider: str = 'deterministic'
    llm_api_key: str = ''
    gemini_api_key: str = ''
    gemini_model: str = 'gemini-3.5-flash'
    gemini_search_enabled: bool = True
    app_env: str = 'development'
    frontend_url: str = 'http://localhost:3000'
    @model_validator(mode='after')
    def check_secret(self):
        if len(self.jwt_secret) < 32:
            raise ValueError('JWT_SECRET must contain at least 32 characters; configure .env')
        if self.jwt_algorithm != 'HS256':
            raise ValueError('Only HS256 is supported in V1')
        return self

settings = Settings()
