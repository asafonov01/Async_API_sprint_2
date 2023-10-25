import json
from uuid import UUID

import pytest

from functional.models.api_models import APIPersonFull, APIPersonShort, APIPersonFilmworks
from functional.models.es_models import ESPerson
from functional.models.response_model import HTTPResponse
from functional.utils.auxiliary import (get_exist_index_id,
                                        get_json_from_file, get_model_by_id,
                                        get_model_list_from_json,
                                        get_models_and_ids,
                                        get_page_parameters,
                                        get_page_parameters_404, get_es_model_by_id)
from settings import DEFAULT_PAGE_SIZE


@pytest.fixture(scope='session')
def test_data_person(settings) -> json:
    return get_json_from_file(settings.person_path)


@pytest.fixture(scope='session')
def model_list_person_input(test_data_person) -> list[ESPerson]:
    return get_model_list_from_json(ESPerson, test_data_person)


@pytest.fixture(scope='session')
def model_list_person(model_list_person_input) -> list[APIPersonFull]:
    persons = [
        APIPersonFull(
            uuid=person.id,
            full_name=person.name,
            filmworks=[APIPersonFilmworks(
                role=pfw.role,
                filmworks=[fw.id for fw in pfw.filmworks]
            ) for pfw in person.filmworks]
        ) for person in model_list_person_input]
    return persons


@pytest.fixture(scope='session')
def model_list_person_input(test_data_person) -> list[ESPerson]:
    return get_model_list_from_json(ESPerson, test_data_person)


@pytest.fixture(scope='session')
def get_model_list_person_short(model_list_person):
    def inner(model_list: list[APIPersonFull]) -> list[APIPersonShort]:
        ids = [model.uuid for model in model_list]
        models = [APIPersonShort(
            uuid=person.uuid,
            full_name=person.full_name
        ) for person in model_list_person if person.uuid in ids]
        return models

    return inner


@pytest.fixture(scope='class')
async def provide_es_index_data_person(settings,
                                       load_es_data,
                                       clear_data_es_redis,
                                       model_list_person_input):
    await load_es_data(model_list_person_input, settings.elastic_index_person)
    yield
    await clear_data_es_redis(settings.elastic_index_person)


@pytest.fixture(scope='session')
def exist_person_id(model_list_person) -> UUID:
    return get_exist_index_id(model_list_person)


@pytest.fixture(scope='session')
def exist_person_model(model_list_person, exist_person_id) -> APIPersonFull:
    return get_model_by_id(model_list_person, exist_person_id)


@pytest.fixture(scope='session')
def create_es_persons(settings,
                      model_list_person_input,
                      exist_person_id,
                      create_es_docs):
    async def inner(person_ids: list[UUID] = None):
        if person_ids:
            models = [
                get_es_model_by_id(model_list_person_input, person_id)
                for person_id in person_ids]
        else:
            models = get_es_model_by_id(model_list_person_input, exist_person_id)
        await create_es_docs(settings.elastic_index_person, models)

    return inner


@pytest.fixture(scope='session')
def delete_es_persons(settings,
                      exist_person_id,
                      delete_es_docs):
    async def inner(person_ids: list[str] = None):
        data = person_ids if person_ids else exist_person_id
        await delete_es_docs(settings.elastic_index_person, data)

    return inner


@pytest.fixture(scope='class')
def person_list_parameters(model_list_person):
    person_count = len(model_list_person)
    params = [({}, DEFAULT_PAGE_SIZE), ]
    params += get_page_parameters(person_count)
    return params


@pytest.fixture(scope='class')
def person_list_params_404(model_list_person):
    person_count = len(model_list_person)
    params = get_page_parameters_404(person_count)
    return params


@pytest.fixture(scope='class')
def person_film_params_404(exist_person_model) -> list[dict]:
    film_count = len(exist_person_model.filmworks)
    assert film_count > 0
    params = [get_page_parameters_404(film_count),
              get_page_parameters_404(film_count, {'sort': 'imdb_rating'}),
              get_page_parameters_404(film_count, {'sort': '-imdb_rating'})]
    return params


@pytest.fixture(scope='class')
def person_film_parameters(exist_person_model) -> list[tuple[dict, int]]:
    film_count = len(exist_person_model.filmworks)
    assert film_count > 0
    params = [({}, min(DEFAULT_PAGE_SIZE, film_count)), ]
    params += get_page_parameters(film_count)
    params += get_page_parameters(film_count, {'sort': 'imdb_rating'})
    params += get_page_parameters(film_count, {'sort': '-imdb_rating'})
    return params


@pytest.fixture(scope='class')
def assert_person_detail(assert_single_response, exist_person_model):
    async def inner(query):
        await assert_single_response(query, APIPersonFull, exist_person_model)

    return inner


@pytest.fixture(scope='class')
def assert_person_list(make_get_request,
                       get_model_list_person_short,
                       assert_response_equal_base_models,
                       assert_status_len,
                       person_sort_key):
    async def inner(query, parameters, page_size) -> list[UUID]:
        response: HTTPResponse = await make_get_request(query, parameters)
        assert_status_len(response, page_size)

        response_models, person_ids = get_models_and_ids(
            response, APIPersonFull)
        base_models = get_model_list_person_short(response_models)
        assert_response_equal_base_models(response_models, base_models,
                                          person_sort_key)
        return person_ids

    return inner
