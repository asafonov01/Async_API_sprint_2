from http import HTTPStatus
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import UUID4

from api.v1.films import SortField
from models.api_models import (
    APIFilmShort,
    APIPersonFilmworks,
    APIPersonFull,
    APIPersonShort,
    APIPaginator,
    get_paginator,
)
from services.films import APIFilmServiceFactory, FilmService
from services.persons import APIPersonServiceFactory, PersonService
from utilites.messages import API_PERSON_NOT_FOUND

router = APIRouter()


# Метод для обработки запроса на список всех фильмов
@router.get("/")
async def persons_all(
        paginator: APIPaginator = Depends(get_paginator),
        person_service: PersonService = Depends(APIPersonServiceFactory.get_service),
) -> List[APIPersonShort]:
    persons = await person_service.get_all(
        page_size=paginator.page_size,
        page_number=paginator.page_number,
    )
    return_data = [
        APIPersonShort(
            uuid=person.id,
            full_name=person.name,
        )
        for person in persons
    ]
    return return_data


# Метод для обработки запросов на поиск по персонам
@router.get("/search")
async def persons_search(
        query: str,
        paginator: APIPaginator = Depends(get_paginator),
        person_service: PersonService = Depends(APIPersonServiceFactory.get_service),
) -> List[APIPersonFull]:
    persons = await person_service.search(
        search_string=query,
        page_size=paginator.page_size,
        page_number=paginator.page_number,
    )
    return [
        APIPersonFull(
            uuid=person.id,
            full_name=person.name,
            film_ids=[
                APIPersonFilmworks(
                    role=role_fw.role,
                    filmworks=[fw.id for fw in role_fw.filmworks],
                )
                for role_fw in person.filmworks
            ],
        )
        for person in persons
    ]


# Метод для обработки запроса данных персоны по идентификатору
@router.get("/{person_id}", response_model=APIPersonFull)
async def person_details(
        person_id: UUID4,
        person_service: PersonService = Depends(APIPersonServiceFactory.get_service),
) -> APIPersonFull:
    person = await person_service.get_by_id(person_id)
    if not person:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=API_PERSON_NOT_FOUND.format(uuid=person_id),
        )
    return APIPersonFull(
        uuid=person.id,
        full_name=person.name,
        film_ids=[
            APIPersonFilmworks(
                role=role_fw.role,
                filmworks=[fw.id for fw in role_fw.filmworks],
            )
            for role_fw in person.filmworks
        ],
    )


# Метод для обработки запроса всех фильмов по персоне
@router.get("/{person_id}/films")
async def films_by_person(
        person_id: UUID4,
        sort: SortField = SortField.rating_desc,
        person_service: PersonService = Depends(APIPersonServiceFactory.get_service),
        film_service: FilmService = Depends(APIFilmServiceFactory.get_service),
        paginator: APIPaginator = Depends(get_paginator),
) -> List[APIFilmShort]:
    films = await person_service.get_list(
        sort_field=sort,
        object_id=person_id,
        film_service=film_service,
        page_size=paginator.page_size,
        page_number=paginator.page_number
    )
    return [
        APIFilmShort(
            uuid=film.id,
            title=film.title,
            imdb_rating=film.imdb_rating,
        )
        for film in films
    ]
