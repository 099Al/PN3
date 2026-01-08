import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    POSTGRES_HOST: str
    POSTGRES_PORT: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    DATABASE_ENGINE: str = 'postgresql+asyncpg'

    API_USER: str
    API_KEY: str
    API_SECRET: str

    path_root: str = str(Path(__file__).resolve().parent.parent)
    path_env: str = str(Path(__file__).resolve().parent.parent / '.env')
    model_config = SettingsConfigDict(env_file=path_env, env_file_encoding="utf-8", extra="ignore")

    # CALC_MODE: str = "EMULATION"
    CALC_MODE: str = "API"

    @property
    def connect_url(self):
        return f'{self.DATABASE_ENGINE}://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}'

prj_configs = Config()