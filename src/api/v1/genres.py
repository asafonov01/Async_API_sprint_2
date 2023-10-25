from http import HTTPStatus
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import UUID4

from models.api_models import APIGenre, APIPaginator, get_paginator
from services.genres import APIGenreServiceFactory, GenreService
from utilites.messages import API_GENRE_NOT_FOUND

router = APIRouter()


@router.get("/")
async def genres_all(
        paginator: APIPaginator = Depends(get_paginator),
        genre_service: GenreService = Depends(APIGenreServiceFactory.get_service),
) -> List[APIGenre]:
    genres = await genre_service.get_all(
        page_size=paginator.page_size,
        page_number=paginator.page_number,
    )
    return_data = [
        APIGenre(
            uuid=genre.id,
            name=genre.name,
        )
        for genre in genres
    ]

    return return_data


@router.get("/{genre_id}")
async def genre_by_id(
        genre_id: UUID4,
        genre_service: GenreService = Depends(APIGenreServiceFactory.get_service),
) -> APIGenre:
    genre = await genre_service.get_by_id(genre_id)
    if not genre:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=API_GENRE_NOT_FOUND.format(uuid=genre_id),
        )

    return APIGenre(
        uuid=genre.id,
        name=genre.name,
    )
