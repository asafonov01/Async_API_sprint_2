from typing import List, Type

from pydantic import BaseModel

from lib.models.db import PGBaseModel
from lib.providers.extractor import DBExtractor
from lib.providers.loader import Loader
from lib.providers.transformers import DataTransformer


class FilterData(BaseModel):
    # Фильтрующий запрос для поиска подходящих ID сущности
    query: str
    # имя параметра для подстановки в запрос
    param: str
    # имя ключа для хренения состояния
    state_key: str


class Pipeline(BaseModel):
    """
    Структура собирающая необходимых провайдеров и данные для формирования Пайплайна
    """

    name: str
    extractor: DBExtractor
    transformer: DataTransformer
    loader: Loader

    # Набор опций для отбора сущностей
    filters: List[FilterData]

    # Модель данных выгружаемых из БД
    model: Type[PGBaseModel]

    # Основной запрос для выборки нужных полей по ID сущности
    collect_query: str

    class Config:
        arbitrary_types_allowed = True
