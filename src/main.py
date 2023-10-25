import json
import logging
import time
from contextlib import asynccontextmanager

import aioredis
import uvicorn
from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.responses import ORJSONResponse

from api.v1 import genres, films, persons
from core.config import config
from core.logger import LOGGING
from db import elastic, redis
from services.films import FILM_CACHE_EXPIRE_IN_SECONDS
from utilites.async_iterator_wrapper import AsyncIteratorWrapper

app = FastAPI(
    title=config.PROJECT_NAME,
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    FastAPI(lifespan=lifespan)
    redis.redis = await aioredis.Redis(
        host=config.REDIS_HOST, port=config.REDIS_PORT)

    elastic.es = AsyncElasticsearch(
        hosts=f"{config.ELASTIC_SCHEME}://{config.ELASTIC_HOST}:{config.ELASTIC_PORT}"
    )


@app.on_event("shutdown")
async def shutdown():
    await redis.redis.close()
    await elastic.es.close()


@app.middleware("http")
async def cache_middleware(request: Request, call_next):
    """
    Получение и сохранение результат запроса из кэша Redis
    :param request: Объект запроса из которого берется ключ кэширования
    :param call_next: Метод роутера, формирующий ответ. Используем его для сохранения
    :return:
    """
    start_time = time.time()
    cache_key = "?".join([request["path"], request["query_string"].decode("utf-8")])
    cached_result = await redis.redis.get(cache_key)

    if cached_result:
        process_time = time.time() - start_time
        response = ORJSONResponse(json.loads(cached_result.decode()))
        response.headers["X-Process-Time"] = str(process_time)
        return response

    response = await call_next(request)
    # Consuming FastAPI response and grabbing body here
    resp_body = [section async for section in response.body_iterator]
    # Repairing FastAPI response
    response.__setattr__("body_iterator", AsyncIteratorWrapper(resp_body))

    await redis.redis.set(
        name=cache_key,
        value=resp_body[0].decode(),
        ex=FILM_CACHE_EXPIRE_IN_SECONDS,
    )

    logging.info("Request result cached.")

    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


app.include_router(films.router, prefix="/api/v1/films", tags=["films"])
app.include_router(genres.router, prefix="/api/v1/genres", tags=["genres"])
app.include_router(persons.router, prefix="/api/v1/persons", tags=["persons"])

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        log_config=LOGGING,
        log_level=logging.DEBUG
    )
