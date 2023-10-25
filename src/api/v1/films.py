from enum import Enum
from http import HTTPStatus
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import UUID4

from models.api_models import APIFilmFull, APIFilmShort, APIPaginator, get_paginator
from services.films import APIFilmServiceFactory
from services.films import FilmService
from utilites.messages import API_FILM_NOT_FOUND


class SortField(str, Enum):
    rating_asc = "imdb_rating"
    rating_desc = "-imdb_rating"


# Объект router, в котором регистрируем обработчики
router = APIRouter()


# Метод для обработки запроса на список фильмов
# с опциональной фильтрацией и пагинацией
@router.get("/")
async def films_sorted(
        sort: SortField = SortField.rating_desc,
        filter_field: UUID4 = Query(default=None, alias="filter[genre]"),
        paginator: APIPaginator = Depends(get_paginator),
        film_service: FilmService = Depends(APIFilmServiceFactory.get_service),
) -> List[APIFilmShort]:
    films = await film_service.get_all(
        sort_field=sort,
        filter_field=filter_field,
        page_size=paginator.page_size,
        page_number=paginator.page_number,
    )
    return_data = [
        APIFilmShort(
            uuid=film.id,
            title=film.title,
            imdb_rating=film.imdb_rating,
        )
        for film in films
    ]

    return return_data


# Метод для обработки запроса на поиск по фильмам
@router.get("/search")
async def films_search(
        query: str,
        paginator: APIPaginator = Depends(get_paginator),
        film_service: FilmService = Depends(APIFilmServiceFactory.get_service),
) -> List[APIFilmShort]:
    films = await film_service.search(
        search_string=query,
        page_size=paginator.page_size,
        page_number=paginator.page_number,
    )
    return [
        APIFilmShort(
            uuid=film.id,
            title=film.title,
            imdb_rating=film.imdb_rating,
        )
        for film in films
    ]


# С помощью декоратора регистрируем обработчик film_details
@router.get("/{film_id}", response_model=APIFilmFull)
async def film_details(
        film_id: UUID4,
        film_service: FilmService = Depends(APIFilmServiceFactory.get_service),
) -> APIFilmFull:
    film = await film_service.get_by_id(film_id)
    if not film:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=API_FILM_NOT_FOUND.format(uuid=film_id),
        )

    response = APIFilmFull(
        uuid=film.id,
        title=film.title,
        imdb_rating=film.imdb_rating,
        description=film.description,
        genre=[
            {
                'uuid': genre.id,
                'name': genre.name
            }
            for genre in film.genre],
        actors=[
            {
                "uuid": actor.id,
                "full_name": actor.name,
            }
            for actor in film.actors
        ],
        writers=[
            {
                "uuid": writer.id,
                "full_name": writer.name,
            }
            for writer in film.writers
        ],
        directors=[
            {
                "uuid": director.id,
                "full_name": director.name,
            }
            for director in film.directors
        ],
    )

    return response
