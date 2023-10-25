from functools import lru_cache
from typing import List, Optional, Type

from elasticsearch import NotFoundError
from fastapi import Depends
from pydantic import UUID4

from core.config import config
from db.elastic import get_elastic
from models.es_models import ESGenre
from services.abstract_services import (
    APIAbstractServiceFactory, 
    APIAsyncSearchEngine, 
    APIService,
)
from services.es_queries import GENRES_QUERY
from services.es_query_parameters import ESQueryParameters


class GenreService(APIService):
    def __init__(self, data_source: APIAsyncSearchEngine) -> None:
        self.data_source = data_source
        self.ES_INDEX_NAME = config.ELASTIC_INDEX_GENRE

    async def get_by_id(
            self,
            object_id: UUID4,
            model: Type[ESGenre] = ESGenre,
    ) -> Optional[ESGenre]:
        try:
            doc = await self.data_source.get(
                index=self.ES_INDEX_NAME,
                id=object_id,
            )
        except NotFoundError:
            return None
        return model(**doc["_source"])

    async def get_all(
            self,
            page_size: int,
            page_number: int,
            model: Type[ESGenre] = ESGenre,
    ) -> List[ESGenre]:
        query = GENRES_QUERY
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


class APIGenreServiceFactory(APIAbstractServiceFactory):
    @staticmethod
    @lru_cache()
    def get_service(
            data_source: APIAsyncSearchEngine = Depends(get_elastic),
    ) -> GenreService:
        return GenreService(data_source)
