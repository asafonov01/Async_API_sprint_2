from logging import config as logging_config
from pathlib import Path

from pydantic import BaseSettings, DirectoryPath, Field

from core.logger import LOGGING

# Применяем настройки логирования
logging_config.dictConfig(LOGGING)


class AppSettings(BaseSettings):
    # Название проекта. Используется в Swagger-документации
    PROJECT_NAME: str = Field(default="movies", env="PROJECT_NAME")
    # Параметры подключения к БД
    REDIS_HOST: str = Field(default="localhost", env="REDIS_HOST")
    REDIS_PORT: str = Field(default="6379", env="REDIS_PORT")
    ELASTIC_SCHEME: str = Field(default="http", env="ELASTIC_SCHEME")
    ELASTIC_HOST: str = Field(default="localhost", env="ELASTIC_HOST")
    ELASTIC_PORT: str = Field(default="9200", env="ELASTIC_PORT")

    # Имена индексов в Elasticsearch
    ELASTIC_INDEX_FILM: str = Field(
        default="movies", env="ELASTIC_INDEX_FILM")
    ELASTIC_INDEX_GENRE: str = Field(
        default="genres", env="ELASTIC_INDEX_GENRE")
    ELASTIC_INDEX_PERSON: str = Field(
        default="persons", env="ELASTIC_INDEX_PERSON")

    # Корень проекта
    BASE_DIR: DirectoryPath = Path(__file__).parent.parent


config = AppSettings()
