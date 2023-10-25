import asyncio
import time
from typing import List

from lib.config import COLLECT_WAIT_TIME, PG_CONN, REDIS_KEY
from lib.db.queries import (filmwork_collect_query,
                            filmwork_filter_by_filmwork_dt,
                            filmwork_filter_by_genre_dt,
                            filmwork_filter_by_person_dt, genres_collect_query,
                            person_collect_query, select_genres_by_update_dt,
                            select_persons_by_update_dt)
from lib.etl_process import ETLProcess, Process
from lib.models.db import FilmWorkGenre, FilmWorkPerson, FilmWorkRecord
from lib.models.etl import FilterData, Pipeline
from lib.providers.extractor import PostgresExtractor
from lib.providers.loader import ElasticsearchLoader
from lib.providers.state import RedisStateProvider
from lib.providers.transformers import (FilmworkTransformer, GenreTransformer,
                                        PersonTransformer)
from lib.utilites import get_logger, load_json_from_file


async def main():
    pg_conn = PostgresExtractor(PG_CONN)
    state_provider = RedisStateProvider(REDIS_KEY)
    await state_provider.load()

    pipelines = [
        Pipeline(
            name="movies_pipeline",
            extractor=pg_conn,
            transformer=FilmworkTransformer(),
            loader=ElasticsearchLoader(
                index="movies",
                index_schema=load_json_from_file("index/movies.json"),
            ),
            filters=[
                FilterData(
                    query=filmwork_filter_by_filmwork_dt,
                    param="dt",
                    state_key="fw_last_filmwork_dt",
                ),
                FilterData(
                    query=filmwork_filter_by_genre_dt,
                    param="dt",
                    state_key="fw_last_genre_dt",
                ),
                FilterData(
                    query=filmwork_filter_by_person_dt,
                    param="dt",
                    state_key="fw_last_person_dt",
                ),
            ],
            model=FilmWorkRecord,
            collect_query=filmwork_collect_query,
        ),
        Pipeline(
            name="persons_pipeline",
            extractor=pg_conn,
            transformer=PersonTransformer(),
            loader=ElasticsearchLoader(
                index="persons",
                index_schema=load_json_from_file("index/persons.json"),
            ),
            filters=[
                FilterData(
                    query=select_persons_by_update_dt,
                    param="dt",
                    state_key="persons_last_dt",
                )
            ],
            model=FilmWorkPerson,
            collect_query=person_collect_query,
        ),
        Pipeline(
            name="genres_pipeline",
            extractor=pg_conn,
            transformer=GenreTransformer(),
            loader=ElasticsearchLoader(
                index="genres",
                index_schema=load_json_from_file("index/genres.json"),
            ),
            filters=[
                FilterData(
                    query=select_genres_by_update_dt,
                    param="dt",
                    state_key="genres_last_dt",
                )
            ],
            model=FilmWorkGenre,
            collect_query=genres_collect_query,
        ),
    ]

    processes: List[Process] = []
    for pipeline in pipelines:
        process = ETLProcess(
            pipeline=pipeline,
            state_provider=state_provider,
            logger=get_logger(pipeline.name),
        )
        processes.append(process)

    while True:
        for process in processes:
            await process.run()

        time.sleep(COLLECT_WAIT_TIME)


if __name__ == "__main__":
    asyncio.run(main())
