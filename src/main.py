import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from api import users
from core.config import settings
from core.logger import LOGGING
from db import db_cache
from db import db_storage
from db.postgres.PostgresStorage import PostgresStorage
from db.redis.RedisCache import RedisCache


@asynccontextmanager
async def lifespan(app: FastAPI):
    db_cache.cache = RedisCache(settings.redis_host, settings.redis_port)
    db_storage.storage = PostgresStorage()
    from models.entity import User  # necessary to create table
    await db_storage.storage.create_schema()

    yield

    await db_cache.cache.close()
    if db_storage.storage:
        await db_storage.storage.purge_schema()
        await db_storage.storage.close()


app = FastAPI(
    title=settings.project_name,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
    lifespan=lifespan
)

if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='localhost',
        log_config=LOGGING,
        log_level=logging.DEBUG
    )
