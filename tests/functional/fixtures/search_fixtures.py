import pytest
from elasticsearch import AsyncElasticsearch

from functional.models.api_models import APIFilmShort, APIPersonShort
from functional.utils.auxiliary import (HTTPResponse, get_models_and_ids,
                                        get_page_parameters,
                                        get_page_parameters_404)
from settings import ES_PAGE_MAX_SIZE


@pytest.fixture(scope='session')
def make_get_es_query_count(es_client: AsyncElasticsearch):
    async def inner(index: str, body: dict) -> int:
        page_params = {"from": 0, "size": ES_PAGE_MAX_SIZE}
        body = body | page_params
        docs = await es_client.search(
            index=index,
            body=body
        )
        result_count = len(docs['hits']['hits'])
        assert result_count > 0
        return result_count

    return inner


@pytest.fixture(scope='class')
async def len_film_search_list(make_get_es_query_count, exist_film_model, settings):
    search_fields = ['title', 'description']
    query = exist_film_model.title
    body = {
        "query": {
            "multi_match": {
                "query": query,
                "fields": search_fields
            }
        }
    }
    index = settings.elastic_index_film
    return await make_get_es_query_count(index, body)


@pytest.fixture(scope='class')
async def len_person_search_list(make_get_es_query_count,
                                 exist_person_model,
                                 settings):
    search_field = 'name'
    query = exist_person_model.full_name
    body = {
        "query": {
            "bool": {
                "must": [
                    {"match": {search_field: query}}
                ]
            }
        }
    }
    index = settings.elastic_index_person
    return await make_get_es_query_count(index, body)


@pytest.fixture(scope='class')
def assert_search_film(make_get_request,
                       exist_film_model,
                       assert_response_equal_base_models,
                       film_sort_key,
                       assert_status_len,
                       get_model_list_movie_short):
    async def inner(url: str, parameters: dict, page_size: int):
        response: HTTPResponse = await make_get_request(url, parameters)
        assert_status_len(response, page_size)
        response_models, response_ids = get_models_and_ids(response, APIFilmShort)
        base_models = get_model_list_movie_short(response_models)
        assert_response_equal_base_models(response_models, base_models,
                                          film_sort_key)
        if parameters['page[number]'] == 0:
            assert exist_film_model.uuid == response_ids[0]
        return response_ids

    return inner


@pytest.fixture(scope='class')
def assert_search_person(make_get_request,
                         get_model_list_person_short,
                         assert_response_equal_base_models,
                         assert_status_len,
                         person_sort_key):
    async def inner(url: str, parameters: dict, page_size: int):
        response: HTTPResponse = await make_get_request(url, parameters)
        assert_status_len(response, page_size)

        response_models, response_ids = get_models_and_ids(
            response, APIPersonShort)
        base_models = get_model_list_person_short(response_models)
        assert_response_equal_base_models(response_models, base_models,
                                          person_sort_key)
        return response_ids

    return inner


@pytest.fixture(scope='class')
def film_search_params(len_film_search_list) -> list[tuple[dict, int]]:
    return get_page_parameters(len_film_search_list)


@pytest.fixture(scope='class')
def person_search_params(len_person_search_list) -> list[tuple[dict, int]]:
    return get_page_parameters(len_person_search_list)


@pytest.fixture(scope='class')
def film_search_params_404(len_film_search_list) -> dict:
    return get_page_parameters_404(len_film_search_list)


@pytest.fixture(scope='class')
def person_search_params_404(len_person_search_list) -> dict:
    return get_page_parameters_404(len_person_search_list)
