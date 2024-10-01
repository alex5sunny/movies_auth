from pydantic_settings import BaseSettings
from pydantic import Field
import os
from logging import config as logging_config

from core.logger import LOGGING

logging_config.dictConfig(LOGGING)


class Settings(BaseSettings):
    project_name: str = Field('movies_auth', env='PROJECT_NAME')

    redis_host: str = Field('redis', env='REDIS_HOST')
    redis_port: int = Field(6379, env='REDIS_PORT')

    base_dir: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    cache_expire_in_seconds: int = 5

    postgres_db: str = Field('postgres', env='POSTGRES_DB')
    postgres_user: str = Field('postgres', env='POSTGRES_USER')
    postgres_password: str = Field('postgres', env='POSTGRES_PASSWORD')
    db_host: str = Field('127.0.0.1', env='DB_HOST')
    db_port: int = Field(5434, env='DB_PORT')

    @property
    def dsn(self) -> dict:
        return {
            "dbname": self.db_name,
            "user": self.db_user,
            "password": self.db_password,
            "host": self.db_host,
            "port": self.db_port,
            "options": "-c search_path=content",
        }

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


settings = Settings()
