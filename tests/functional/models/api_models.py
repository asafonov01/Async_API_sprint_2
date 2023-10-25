from typing import List, Optional

from pydantic import UUID4

from functional.models.base_model import OrjsonBase


class APIBaseModel(OrjsonBase):
    uuid: UUID4


class APIPersonFilmworks(OrjsonBase):
    role: str
    filmworks: List[UUID4]


class APIGenre(APIBaseModel):
    name: str


class APIPersonShort(APIBaseModel):
    full_name: str


class APIPersonFull(APIPersonShort):
    filmworks: Optional[List[APIPersonFilmworks]]


class APIFilmShort(APIBaseModel):
    title: str
    imdb_rating: Optional[float] = 0.0


class APIFilmFull(APIFilmShort):
    description: Optional[str]
    genre: Optional[List[APIGenre]]
    actors: Optional[List[APIPersonShort]]
    writers: Optional[List[APIPersonShort]]
    directors: Optional[List[APIPersonShort]]
