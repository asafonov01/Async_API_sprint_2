from typing import List, Optional

from fastapi import Query
from pydantic import BaseModel, UUID4


class APIPaginator(BaseModel):
    page_size: int
    page_number: int


class APIBaseModel(BaseModel):
    uuid: UUID4


class APIPersonFilmworks(BaseModel):
    role: str
    filmworks: List[UUID4]


class APIGenre(APIBaseModel):
    name: str


class APIPersonShort(APIBaseModel):
    full_name: str


class APIPersonFull(APIPersonShort):
    film_ids: Optional[List[APIPersonFilmworks]]


class APIFilmShort(APIBaseModel):
    title: str
    imdb_rating: Optional[float] = 0.0


class APIFilmFull(APIFilmShort):
    description: Optional[str]
    genre: Optional[List[APIGenre]]
    actors: Optional[List[APIPersonShort]]
    writers: Optional[List[APIPersonShort]]
    directors: Optional[List[APIPersonShort]]


def get_paginator(
        page_size: int = Query(default=10, alias="page[size]", ge=1, le=10000),
        page_number: int = Query(default=1, alias="page[number]", ge=1, le=10000),
) -> APIPaginator:
    return APIPaginator(page_size=page_size, page_number=page_number)
