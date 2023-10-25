from abc import ABC, abstractmethod
from typing import List

from elasticsearch import Elasticsearch, helpers

from lib.config import CLEAN_ELASTIC_ON_START, ES_HOST, logger
from lib.models.es import ESBaseModel
from lib.utilites import backoff


class Loader(ABC):
    @abstractmethod
    def load(self, transformed_data: List[ESBaseModel]):
        ...


class ElasticsearchLoader(Loader):
    def __init__(self, index: str, index_schema: dict):
        self.index_name = index
        self.index_schema = index_schema
        self.es = Elasticsearch(hosts=[ES_HOST])
        self.__init_index()

    @backoff(logger=logger)
    def load(self, transformed_data: List[ESBaseModel]):
        actions = []
        for item in transformed_data:
            exists = self.es.exists(index=self.index_name, id=str(item.id))
            action = {
                "_index": self.index_name,
                "_op_type": "update" if exists else "create",
                "_id": item.id,
            }
            if exists:
                action.update({"doc": item.dict()})
            else:
                action.update({"_source": item.dict()})
            actions.append(action)

        return helpers.bulk(self.es, actions, stats_only=True)

    @backoff(logger=logger)
    def __init_index(self):
        if CLEAN_ELASTIC_ON_START:
            self.es.indices.delete(index=self.index_name)

        if not self.es.indices.exists(index=self.index_name):
            self.es.indices.create(index=self.index_name, body=self.index_schema)
            logger.info(f"Index {self.index_name} created")
        else:
            logger.info(f"Index {self.index_name} already exists")
