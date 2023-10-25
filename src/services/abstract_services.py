from abc import ABC, abstractmethod
from typing import List, Type

from pydantic import UUID4

from models.es_models import ESBaseModel


class APIService(ABC):
    @abstractmethod
    def get_by_id(
        self,
        object_id: UUID4,
        model: Type[ESBaseModel] = ESBaseModel,
    ) -> ESBaseModel:
        ...

    @abstractmethod
    def get_all(
        self,
        page_size: int = None,
        page_number: int = None,
        model: Type[ESBaseModel] = ESBaseModel,
        **kwargs,
    ) -> List[ESBaseModel]:
        ...


class APIServiceListable(APIService):
    @abstractmethod
    def get_list(
        self,
        model: Type[ESBaseModel] = ESBaseModel,
        **kwargs,
    ) -> List[ESBaseModel]:
        ...


class APIServiceSearchable(APIService):
    @abstractmethod
    def search(
        self,
        search_string: str,
        page_size: int = None,
        page_number: int = None,
        model: Type[ESBaseModel] = ESBaseModel,
    ) -> List[ESBaseModel]:
        ...


class APIAsyncSearchEngine(ABC):
    @abstractmethod
    async def get(self, index: str, id: str, **kwargs):
        ...

    @abstractmethod
    async def search(self, index: str, body: str, **kwargs):
        ...
    
    @abstractmethod
    async def mget(self, index: str, body: dict, **kwargs):
        ...


class APIAbstractServiceFactory(ABC):
    @staticmethod
    @abstractmethod
    def get_service(
        data_source: APIAsyncSearchEngine = APIAsyncSearchEngine,
    ):
        ...