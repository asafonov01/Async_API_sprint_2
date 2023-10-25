from typing import List

from pydantic import UUID4, BaseModel


class ESIdModel(BaseModel):
    id: UUID4


class ESBaseModel(BaseModel):
    id: UUID4 = None


class ESFilmWorkGenre(ESBaseModel):
    name: str = None
    description: str = None


class ESPersonFilmworks(BaseModel):
    role: str
    filmworks: List[ESIdModel]


class ESFilmWorkPerson(ESBaseModel):
    name: str = None


class ESFilmworkPersonWithFilmworks(ESFilmWorkPerson):
    filmworks: List[ESPersonFilmworks] = None


class ESFilmWorkGenresItem(BaseModel):
    id: UUID4
    name: str


class ESFilmWorkRecord(ESBaseModel):
    imdb_rating: float = 0.0
    genre: List[ESFilmWorkGenresItem] = None
    title: str = None
    description: str = None
    actors_names: str = None
    writers_names: str = None
    directors: List[ESFilmWorkPerson] = None
    actors: List[ESFilmWorkPerson] = None
    writers: List[ESFilmWorkPerson] = None
