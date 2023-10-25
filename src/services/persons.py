from functools import lru_cache
from typing import List, Optional, Type

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from pydantic import UUID4

from core.config import config
from db.elastic import get_elastic
from models.es_models import ESFilm, ESPerson
from services.abstract_services import (
    APIAbstractServiceFactory,
    APIAsyncSearchEngine,
    APIServiceListable,
    APIServiceSearchable,
)
from services.es_queries import PERSONS_SEARCH_QUERY, PERSONS_QUERY
from services.es_query_parameters import ESQueryParameters
from services.films import FilmService


class PersonService(APIServiceListable, APIServiceSearchable):
    def __init__(self, data_source: APIAsyncSearchEngine) -> None:
        self.data_source = data_source
        self.ES_INDEX_NAME = config.ELASTIC_INDEX_PERSON

    # Метод для получения персоны по идентификатору
    async def get_by_id(
            self,
            object_id: UUID4,
            model: Type[ESPerson] = ESPerson,
    ) -> Optional[ESPerson]:
        try:
            doc = await self.data_source.get(
                index=self.ES_INDEX_NAME,
                id=str(object_id),
            )
            return_data = model(**doc["_source"])
        except NotFoundError:
            return None

        return return_data

    async def get_all(
            self,
            page_size: int,
            page_number: int,
            model: Type[ESPerson] = ESPerson,
    ) -> List[ESPerson]:
        query = PERSONS_QUERY
        query.update(
            ESQueryParameters.get_es_pagination_parameters(
                page_size,
                page_number,
            )
        )
        raw_data = await self.data_source.search(
            index=self.ES_INDEX_NAME,
            body=query,
        )
        return_data = [
            model(**hit["_source"]) for hit in raw_data["hits"]["hits"]
        ]
        return return_data

    async def get_list(
            self,
            sort_field: str,
            object_id: UUID4,
            film_service: FilmService,
            page_size: int = None,
            page_number: int = None,
    ) -> List[ESFilm]:
        person = await self.get_by_id(object_id)
        if not person:
            return []
        film_ids = set()
        for rfw in person.filmworks:
            film_ids.update([fw.id for fw in rfw.filmworks])

        return await film_service.get_list(objects_list=list(film_ids),
                                           page_size=page_size,
                                           page_number=page_number)

    async def search(
            self,
            search_string: str,
            page_size: int = None,
            page_number: int = None,
    ) -> List[ESPerson]:
        query = PERSONS_SEARCH_QUERY
        query["query"]["match"]["name"]["query"] = search_string
        if page_size and page_number:
            query.update(
                ESQueryParameters.get_es_pagination_parameters(
                    page_size,
                    page_number,
                )
            )
        raw_data = await self.data_source.search(
            index=self.ES_INDEX_NAME,
            body=query,
        )
        return_data = [
            ESPerson(**hit["_source"]) for hit in raw_data["hits"]["hits"]
        ]
        return return_data


class APIPersonServiceFactory(APIAbstractServiceFactory):
    @staticmethod
    @lru_cache()
    def get_service(
            data_source: APIAsyncSearchEngine = Depends(get_elastic),
    ) -> PersonService:
        return PersonService(data_source)
