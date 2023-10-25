from typing import List, Optional

import orjson
# Используем pydantic для упрощения работы при перегонке данных из json в объекты
from pydantic import UUID4, BaseModel


def orjson_dumps(v, *, default):
    # orjson.dumps возвращает bytes, а pydantic требует unicode, поэтому декодируем
    return orjson.dumps(v, default=default).decode()


class ESBaseOrjsonModel(BaseModel):
    class Config:
        # Заменяем стандартную работу с json на более быструю
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class ESBaseModel(ESBaseOrjsonModel):
    id: UUID4


class ESPersonFilmworks(ESBaseOrjsonModel):
    role: str
    filmworks: List[ESBaseModel]


class ESGenre(ESBaseModel):
    name: str
    description: Optional[str]


class ESPerson(ESBaseModel):
    name: str
    filmworks: Optional[List[ESPersonFilmworks]]


class ESFilm(ESBaseModel):
    id: str
    imdb_rating: Optional[float]
    genre: Optional[List[ESGenre]]
    title: str
    description: Optional[str]
    directors: Optional[List[ESPerson]]
    actors_names: Optional[str]
    writers_names: Optional[str]
    actors: Optional[List[ESPerson]]
    writers: Optional[List[ESPerson]]
