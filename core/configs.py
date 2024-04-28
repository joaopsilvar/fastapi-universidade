from typing import List
from pydantic_settings import BaseSettings,SettingsConfigDict
from sqlalchemy.ext.declarative import declarative_base,DeclarativeMeta

class Settings(BaseSettings):
    API_V1_STR: str = '/api/v1'
    DB_URL:str = 'postgresql+asyncpg://postgres:123456@localhost:5432/faculdade'
    DBBaseModel: DeclarativeMeta = declarative_base()

    JWT_SECRET: str = 'xz-f82ABlHx-jK4QHyEtppbki7jnDcV5jI_1cHDsw6Q'
    ALGORITHM: str = 'HS256'
    # 60 minutos * 24 horas * 7 dias => 1 semana
    ACCESS_TOKEN_EXPIRE_MINUTOS: int = 60 * 24 * 7
    
    model_config = SettingsConfigDict(case_sensitive=True)


settings: Settings = Settings()