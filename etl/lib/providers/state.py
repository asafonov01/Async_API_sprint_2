import json
from abc import ABC, abstractmethod

import aioredis

from lib.config import CLEAN_REDIS_ON_START, REDIS_CONN


class BaseStateProvider(ABC):
    @abstractmethod
    def load(self):
        """Loading whole state from its storage"""
        ...

    @abstractmethod
    def save(self):
        """Saving whole state to its storage"""
        ...

    @abstractmethod
    def get(self, key: str):
        """Getting value of recieved key from state"""
        ...

    @abstractmethod
    def set(self, key: str, value: str):
        """Saving key-value pair to state"""
        ...


class RedisStateProvider(BaseStateProvider):

    async def save(self):
        return await self.redis.set(name=self.key, value=json.dumps(self.state))

    async def get(self, key: str):
        return self.state.get(key)

    async def set(self, key: str, value: str):
        self.state[key] = value
        await self.save()

    async def load(self):
        if CLEAN_REDIS_ON_START:
            await self.redis.delete(self.key)

        data: bytes = await self.redis.get(self.key)
        self.state = json.loads(data or "{}")

    def __init__(self, key: str):
        self.key: str = key
        self.redis = aioredis.from_url(f"redis://{REDIS_CONN['host']}:{REDIS_CONN['port']}")
        self.state: dict = {}
