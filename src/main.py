import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import ORJSONResponse

from api import users, roles
from core.config import settings, Settings
from core.logger import LOGGING
from db import db_cache
from db.postgres import create_database, purge_database
from db.redis.redis_cache import RedisCache


@asynccontextmanager
async def lifespan(app: FastAPI):
    db_cache.cache = RedisCache()

    yield

    await db_cache.cache.close()


app = FastAPI(
    title=settings.project_name,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
    lifespan=lifespan
)


app.include_router(users.router, prefix='/api/users', tags=['users'])
app.include_router(roles.router, prefix='/api/roles', tags=['roles'])

if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='localhost',
        log_config=LOGGING,
        log_level=logging.DEBUG
    )
