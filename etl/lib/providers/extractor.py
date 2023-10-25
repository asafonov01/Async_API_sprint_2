from abc import ABC, abstractmethod
from contextlib import contextmanager
from typing import Type

import psycopg2
from psycopg2.extras import DictCursor

from lib.config import DB_CHUNK_SIZE, logger
from lib.models.db import PGBaseModel, PGFilterModel
from lib.utilites import backoff


class DBExtractor(ABC):
    @staticmethod
    @abstractmethod
    def context(connection_dict: dict):
        ...

    @abstractmethod
    def extract(self, query: str, args: dict, model: Type[PGBaseModel] = PGFilterModel):
        ...

    @abstractmethod
    def extract_generator(self, query: str, args: dict, model: Type[PGBaseModel] = PGFilterModel):
        ...


class PostgresExtractor(DBExtractor):

    def __init__(self, dsl: dict):
        self.dsl = dsl

    @staticmethod
    @contextmanager
    def context(conn_dict: dict):
        conn = psycopg2.connect(**conn_dict, cursor_factory=DictCursor)
        yield conn
        conn.commit()
        conn.close()

    @backoff(logger=logger)
    def extract(self, query: str, args: dict, model: Type[PGBaseModel] = PGFilterModel):
        with PostgresExtractor.context(self.dsl) as pg_conn, pg_conn.cursor() as cursor:
            cursor.execute(query, args)
            results = cursor.fetchall()
            return [model(**result) for result in results]

    @backoff(logger=logger)
    def extract_generator(self, query: str, args: dict, model: Type[PGBaseModel] = PGFilterModel):
        with PostgresExtractor.context(self.dsl) as pg_conn, pg_conn.cursor() as cursor:
            cursor.execute(query, args)
            while True:
                results = cursor.fetchmany(DB_CHUNK_SIZE)
                if not results:
                    break
                # noinspection PyArgumentList
                yield [model(**result) for result in results]
