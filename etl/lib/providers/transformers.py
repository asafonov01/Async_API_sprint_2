from abc import ABC, abstractmethod
from typing import List

from lib.models.db import (FilmWorkGenre, FilmWorkPerson, FilmWorkPersonRole,
                           FilmWorkRecord, PersonFilmwork, PGBaseModel)
from lib.models.es import (ESBaseModel, ESFilmWorkGenre, ESFilmWorkPerson,
                           ESFilmworkPersonWithFilmworks, ESFilmWorkRecord)


class DataTransformer(ABC):
    """Абстрактный класс преобразователя данных из БД в ES"""

    @abstractmethod
    def transform(self, src: PGBaseModel) -> ESBaseModel:
        ...


class FilmworkTransformer(DataTransformer):
    def transform(self, src: FilmWorkRecord) -> ESFilmWorkRecord:
        es_record = ESFilmWorkRecord()
        es_record.id = src.id
        es_record.imdb_rating = src.rating
        es_record.genre = [{'id': genre.id, 'name': genre.name} for genre in src.genres]
        es_record.title = src.title
        es_record.description = src.description
        es_record.actors_names = ' '.join(
            [p.person_name for p in src.persons if p.person_role == FilmWorkPersonRole.actor])
        es_record.writers_names = ' '.join(
            [p.person_name for p in src.persons if p.person_role == FilmWorkPersonRole.writer])
        es_record.directors = [{'id': p.person_id, 'name': p.person_name} for p in src.persons if
                               p.person_role == FilmWorkPersonRole.director]
        es_record.actors = [{'id': p.person_id, 'name': p.person_name} for p in src.persons if
                            p.person_role == FilmWorkPersonRole.actor]
        es_record.writers = [{'id': p.person_id, 'name': p.person_name} for p in src.persons if
                             p.person_role == FilmWorkPersonRole.writer]

        return es_record


class PersonTransformer(DataTransformer):
    def transform(self, src: FilmWorkPerson) -> ESFilmWorkPerson:
        es_record = ESFilmworkPersonWithFilmworks()
        es_record.id = src.id
        es_record.name = src.full_name
        es_record.filmworks = self.__group_films_by_role(src.filmworks)
        return es_record

    @staticmethod
    def __group_films_by_role(filmworks: List[PersonFilmwork]):
        result = {}
        for fw in filmworks:
            if fw.role in result.keys():
                result[fw.role].append(fw.filmwork)
            else:
                result[fw.role] = [fw.filmwork]
        return [{'role': k, 'filmworks': [{'id': fw_id} for fw_id in v]} for k, v in result.items()]


class GenreTransformer(DataTransformer):
    def transform(self, src: FilmWorkGenre) -> ESFilmWorkGenre:
        es_record = ESFilmWorkGenre()
        es_record.id = src.id
        es_record.name = src.name
        es_record.description = src.description
        return es_record
