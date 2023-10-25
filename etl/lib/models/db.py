import datetime
from enum import Enum
from typing import List, Optional

from pydantic import UUID4, BaseModel


class PGFilterModel(BaseModel):
    id: UUID4
    modified: datetime.datetime


class PGBaseModel(PGFilterModel):
    created: datetime.datetime


class FilmWorkGenre(PGBaseModel):
    name: str
    description: Optional[str]


class PersonFilmwork(BaseModel):
    role: str
    filmwork: UUID4


class FilmWorkPerson(PGBaseModel):
    full_name: str
    filmworks: List[PersonFilmwork]


class FilmWorkPersonRole(str, Enum):
    actor = "actor"
    director = "director"
    writer = "writer"


class FilmWorkPersonSubItem(BaseModel):
    person_role: FilmWorkPersonRole
    person_id: UUID4
    person_name: str


class FilmWorkGenreSubItem(BaseModel):
    id: UUID4
    name: str


class FilmWorkRecord(PGBaseModel):
    title: str
    description: Optional[str]
    rating: Optional[float]
    type: str
    persons: List[FilmWorkPersonSubItem]
    genres: List[FilmWorkGenreSubItem]
