import asyncio
import json
from pathlib import Path

from elasticsearch import AsyncElasticsearch

total_docs = 10000
dump_path = Path.cwd() / "tests" / "functional" / "testdata"


async def dump_index(es: AsyncElasticsearch, index: str, out_file: str):
    search_result = await es.search(
        index=index,
        body={},
        size=total_docs
    )
    rows = search_result["hits"]["hits"]
    fields = [row['_source'] for row in rows]
    with open(out_file, 'w') as file:
        json.dump(fields, file)


async def main(es: AsyncElasticsearch):
    indexes = ['movies', 'persons', 'genres']
    for index in indexes:
        await dump_index(es, index, out_file=str(dump_path / f"{index}.json"))


if __name__ == '__main__':
    es_provider = AsyncElasticsearch(hosts=["http://localhost:9200"])

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(es_provider))
    loop.close()
