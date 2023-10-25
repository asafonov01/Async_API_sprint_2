from functools import lru_cache
from typing import List, Optional, Type

from elasticsearch import NotFoundError
from fastapi import Depends
from pydantic import UUID4

from core.config import config
from db.elastic import get_elastic
from models.es_models import ESFilm
from services.abstract_services import (
    APIAbstractServiceFactory,
    APIAsyncSearchEngine,
    APIServiceListable,
    APIServiceSearchable,
)
from services.es_queries import (
    FILMS_QUERY,
    FILMS_SEARCH_QUERY,
    GENRE_FILTERED_FILMS_QUERY,
)
from services.es_query_parameters import ESQueryParameters

FILM_CACHE_EXPIRE_IN_SECONDS = 5  # 5 секунд


class FilmService(APIServiceListable, APIServiceSearchable):
    def __init__(self, data_source: APIAsyncSearchEngine):
        self.data_source = data_source
        self.ES_INDEX_NAME = config.ELASTIC_INDEX_FILM

    # get_by_id возвращает объект фильма. Он опционален,
    # так как фильм может отсутствовать в базе
    async def get_by_id(
            self,
            object_id: UUID4,
            model: Type[ESFilm] = ESFilm,
    ) -> Optional[ESFilm]:
        try:
            doc = await self.data_source.get(
                index=self.ES_INDEX_NAME,
                id=object_id,
                _source_excludes=[
                    "actors_names",
                    "writers_names",
                ],
            )
        except NotFoundError:
            return None
        return model(**doc["_source"])

    # Возвращает список фильмов, отсортированный по указанному полю
    async def get_all(
            self,
            sort_field: str,
            filter_field: UUID4 = None,
            page_size: int = None,
            page_number: int = None,
            model: Type[ESFilm] = ESFilm,
    ) -> List[ESFilm]:
        if not filter_field:
            query = FILMS_QUERY
        else:
            query = GENRE_FILTERED_FILMS_QUERY
            match_dict = {"genre.id": filter_field}
            query["query"]["nested"]["query"]["match"] = match_dict

        # Дополняем запрос параметрами пагинации,
        # если указаны page_size и page_number
        query.update(
            ESQueryParameters.get_es_pagination_parameters(
                page_size,
                page_number,
            )
        )
        query["sort"] = ESQueryParameters.get_es_sorting(sort_field)

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
            objects_list: List[UUID4],
            model: Type[ESFilm] = ESFilm,
            page_size: int = None,
            page_number: int = None,
    ) -> List[ESFilm]:
        films = await self.data_source.mget(
            index="movies",
            _source=["id", "title", "imdb_rating"],
            body={"ids": objects_list},
        )
        return_data = [model(**doc["_source"]) for doc in films["docs"]]
        return return_data

    async def search(
            self,
            search_string: str,
            page_size: int = None,
            page_number: int = None,
            model: Type[ESFilm] = ESFilm,
    ) -> List[ESFilm]:

        query = FILMS_SEARCH_QUERY
        query["query"]["multi_match"]["query"] = search_string
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


class APIFilmServiceFactory(APIAbstractServiceFactory):
    @staticmethod
    @lru_cache()
    def get_service(
            data_source: APIAsyncSearchEngine = Depends(get_elastic),
    ) -> FilmService:
        return FilmService(data_source)
