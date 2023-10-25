import datetime
import logging
from abc import ABC, abstractmethod

from lib.models.etl import Pipeline
from lib.providers.state import BaseStateProvider


class Process(ABC):
    """
    Процесс загрузки данных оперирующий несколькими входными параметрами:
        - Хранилище состояния, откуда берется сохраненное состояние по каждой итерации
          для начала следующей итерации с нужного места
        - Экстрактор, позволящий достававть данные из хранилища
        - Трансформер, преобразующий данные в пригодный вид для последующей загрузки
        - Загрузчик, склыдвающий в быстрое хранилище подготовленные данные
    """

    @abstractmethod
    def run(self):
        """Основная точка входа для процесса загрузки данных
        Выполняет итерацию загрузки данных, основываясь на фильтрах и текущем состоянии"""


class ETLProcess(Process):
    def __init__(
            self,
            pipeline: Pipeline,
            state_provider: BaseStateProvider,
            logger: logging.Logger = None,
    ):
        self.pipeline = pipeline

        self.extractor = pipeline.extractor
        self.transformer = pipeline.transformer
        self.loader = pipeline.loader

        self.state = state_provider
        self.logger = logger
        self.__init_logger()

    async def run(self):
        ids = set()
        for f in self.pipeline.filters:
            self.log(f"search by {f.state_key}")
            state = await self.__get_state(f.state_key)
            self.log(f"state: {state}")

            # Выборка всех ID сущности по фильтру
            current_filter_result = self.extractor.extract(
                query=f.query, args={f.param: state}
            )
            if current_filter_result:
                # Сборка уникальных ID
                ids.update({r.id for r in current_filter_result})

                # Сохранение последней обработанной даты в фильтре
                last_filter_dt = max(
                    [r.modified for r in current_filter_result]
                )
                await self.state.set(f.state_key, str(last_filter_dt))
                self.log(f"{f.state_key} now is {last_filter_dt}")

        self.log(f"Collected {len(ids)} ids")

        if ids:
            # Выборка пачками через генератор данные по сущностям
            db_gen = self.extractor.extract_generator(
                query=self.pipeline.collect_query,
                args={"ids": tuple(str(id_) for id_ in ids)},
                model=self.pipeline.model,
            )
            # Загрузка преобразованных данных
            for chunk in db_gen:
                transformed_data = [
                    self.transformer.transform(c) for c in chunk
                ]
                result = self.loader.load(transformed_data)
                self.log(result)
                self.log(f"Loaded {len(chunk)} rows")

        self.log("=" * 50)

    def log(self, msg: str, level=None):
        """Обертка логирования для упрощенного доступа"""
        self.logger.log(level=level or logging.INFO, msg=msg)

    async def __get_state(self, state_key: str):
        value = await self.state.get(state_key)
        if value:
            return datetime.datetime.fromisoformat(value)
        return datetime.datetime.min

    def __init_logger(self):
        if not self.logger:
            self.logger = logging.getLogger(__name__)
