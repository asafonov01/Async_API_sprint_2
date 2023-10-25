import asyncio
import json
from typing import Union
from uuid import UUID

import aiohttp
import aioredis
import pytest
from elasticsearch import AsyncElasticsearch

from functional.models.response_model import HTTPResponse
from functional.utils.auxiliary import OUT_MODEL
from settings import ES_PAGE_MAX_SIZE, ConfTest

pytest_plugins = [
    'functional.fixtures.film_fixtures',
    'functional.fixtures.genre_fixtures',
    'functional.fixtures.person_fixtures',
    'functional.fixtures.search_fixtures',
    'functional.fixtures.assert_fixtures',
]


@pytest.fixture(scope='session')
def settings() -> ConfTest:
    settings = ConfTest()
    return settings


@pytest.fixture(scope='session')
async def es_client(settings):
    client = AsyncElasticsearch(
        hosts=f'{settings.elastic_scheme}://{settings.elastic_host}:{settings.elastic_port}')
    yield client
    await client.close()


@pytest.fixture(scope='session')
async def redis_client(settings):
    client = await aioredis.Redis(
        host=settings.redis_host, port=settings.redis_port)
    yield client
    await client.close()


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope='session')
async def session(event_loop):
    session = aiohttp.ClientSession(loop=event_loop)
    yield session
    await session.close()


@pytest.fixture(scope='session')
def make_get_request(session):
    """
    Предоставляет интерфейс клиента для url запросов к Fastapi
    """

    async def inner(url: str, params: dict = None) -> HTTPResponse:
        params = params or {}
        print(url, params)
        async with session.get(url, params=params) as response:
            return HTTPResponse(
                body=await response.json(),
                headers=response.headers,
                status=response.status,
            )

    return inner


@pytest.fixture(scope='session')
def delete_es_docs(es_client: AsyncElasticsearch):
    async def inner(index: str, data: Union[UUID, list[UUID]]):
        """
        Удаляет выбранные данные из индекса Elasticsearch.
        :param index: Имя индекса в Elasticsearch.
        :param data: UUID документа или Список UUID документов.
        """
        if type(data) is list:
            bulk_body = [
                {'delete': {'_index': index, '_id': x}} for x in data]
            await es_client.bulk(body=bulk_body)
        else:
            doc_id = str(data)
            await es_client.delete(index=index, id=doc_id)
        await es_client.indices.refresh()

    return inner


@pytest.fixture(scope='session')
def create_es_docs(es_client: AsyncElasticsearch):
    async def inner(index: str, data: Union[list[OUT_MODEL], OUT_MODEL]):
        """
        Записывает данные в индекс Elasticsearch из моделей.
        :param index: Имя индекса в Elasticsearch.
        :param data: Модель или список моделей входных моделей.
        """
        if type(data) is list:
            body = []
            for model in data:
                head = {'index': {'_index': index, '_id': model.id}}
                body.append(head)
                body.append(model.dict())
            await es_client.bulk(body=body)
        else:
            await es_client.create(
                index=index, id=data.id, body=data.dict())
        await es_client.indices.refresh()

    return inner


@pytest.fixture(scope='session')
def clear_es_index(es_client: AsyncElasticsearch,
                   make_get_es_index_all_id):
    async def inner(index: str):
        """
        Очистить индекс Elasticsearch от всех документов.
        :param index: Имя индекса в Elasticsearch.
        """
        ids = await make_get_es_index_all_id(index)
        bulk_body = [
            {'delete': {'_index': index, '_id': x}} for x in ids]
        await es_client.bulk(body=bulk_body)
        await es_client.indices.refresh()

    return inner


@pytest.fixture(scope='session')
def clear_data_es_redis(redis_client,
                        clear_es_index):
    async def inner(es_index_name: str):
        """
        Очистка индекса в Elasticsearch, очистка кэша в Redis
        :param es_index_name: Имя индекса в Elasticsearch.
        """
        await redis_client.flushall()
        await clear_es_index(es_index_name)

    return inner


@pytest.fixture(scope='session')
def load_es_data(es_client: AsyncElasticsearch):
    async def inner(data: json, index: str):
        """
        Загрузка тестовых данных в Elasticsearch из файла.
        :param index:
        :param data: Файл с данными.
        """
        body = []
        for model in data:
            head = {'index': {'_index': index, '_id': model.id}}
            body.append(head)
            body.append(model.dict())
        await es_client.bulk(index=index, body=body)
        await es_client.indices.refresh()

    return inner


@pytest.fixture(scope='session')
def make_get_es_index_all_id(es_client: AsyncElasticsearch):
    async def inner(index: str) -> list[UUID]:
        """
        Получает список всех UUID документов в индексе.
        :param index: Имя индекса в Elasticsearch.
        """
        response = await es_client.search(
            index=index,
            filter_path=['hits.hits._id'], from_=0, size=ES_PAGE_MAX_SIZE)
        return [x['_id'] for x in response['hits']['hits']]

    return inner


@pytest.fixture(scope='session')
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
