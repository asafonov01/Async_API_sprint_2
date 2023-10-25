from typing import List, Optional

# Используем pydantic для упрощения работы при перегонке данных из json в объекты
from pydantic import UUID4

from functional.models.base_model import OrjsonBase


class ESBaseModel(OrjsonBase):
    id: UUID4


class ESPersonFilmworks(OrjsonBase):
    role: str
    filmworks: List[ESBaseModel]


class ESFilmworkGenre(ESBaseModel):
    name: str


class ESGenre(ESBaseModel):
    name: str
    description: Optional[str]


class ESPerson(ESBaseModel):
    name: str
    filmworks: Optional[List[ESPersonFilmworks]]


class ESFilworkPerson(ESBaseModel):
    name: str


class ESFilm(ESBaseModel):
    imdb_rating: Optional[float]
    genre: Optional[List[ESFilmworkGenre]]
    title: str
    description: Optional[str]
    directors: Optional[List[ESFilworkPerson]]
    actors_names: Optional[str]
    writers_names: Optional[str]
    actors: Optional[List[ESFilworkPerson]]
    writers: Optional[List[ESFilworkPerson]]
