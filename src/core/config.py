import os
from datetime import datetime
from pydantic_settings import BaseSettings
from pydantic import Field
from logging import config as logging_config
from core.logger import LOGGING

logging_config.dictConfig(LOGGING)

with open('diagnosis.txt', 'a') as f:
    print("{0} при загрузке объекта Settings переменные окружения следующие: {1}"
          .format(datetime.now(), os.environ.copy()), file=f)

class Settings(BaseSettings):
    class Config:
        env_file = '../configs/.env.dev'
        env_file_encoding = 'utf-8'

    project_name: str = Field('movies_auth', alias='PROJECT_NAME')

    redis_host: str = Field('redis', alias='REDIS_HOST')
    redis_port: int = Field(6379, alias='REDIS_PORT')

    base_dir: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    cache_expire_in_seconds: int = 5

    postgres_db: str = Field('postgres', alias='POSTGRES_DB')
    postgres_user: str = Field('postgres', alias='POSTGRES_USER')
    postgres_password: str = Field('postgres', alias='POSTGRES_PASSWORD')
    db_host: str = Field('127.0.0.1', alias='DB_HOST')
    db_port: int = Field(5432, alias='DB_PORT')



    secret_key: str = Field('q!@#j4k3l2m9z8y7x6v5u4t3s2r1p0', alias='SECRET_KEY')
    access_token_lifetime: int = Field(15, alias='ACCESS_TOKEN_LIFETIME')
    refresh_token_lifetime: int = Field(14400, alias='REFRESH_TOKEN_LIFETIME')
    algorithm: str = Field('HS256', alias='ALGORITHM')

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


settings = Settings()

with open('diagnosis.txt', 'a') as f:
    print("{0} при загрузке объекта Settings self.postgres_db следующая: {1}"
          .format(datetime.now(), settings.postgres_db), file=f)