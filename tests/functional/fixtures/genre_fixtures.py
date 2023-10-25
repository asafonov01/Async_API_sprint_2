import json
from uuid import UUID

import pytest as pytest

from functional.models.api_models import APIGenre
from functional.models.es_models import ESGenre
from functional.models.response_model import HTTPResponse
from functional.utils.auxiliary import (get_exist_index_id,
                                        get_json_from_file, get_model_by_id,
                                        get_model_list_from_json,
                                        get_models_and_ids,
                                        get_page_parameters,
                                        get_page_parameters_404, get_es_model_by_id)
from settings import DEFAULT_PAGE_SIZE, ConfTest


@pytest.fixture(scope='session')
def test_data_genre(settings: ConfTest) -> json:
    return get_json_from_file(settings.genre_path)


@pytest.fixture(scope='session')
def model_list_genre_input(test_data_genre) -> list[ESGenre]:
    """
        Список базовых входных моделей, получаемый из тестового файла.
        Используется для загрузки в данных в Elasticsearch при тестировании кэша
        (когда требуется удалять и записывать часть данных, а не все).
        :param test_data_genre: Файл с тестовыми данными.
        """
    return get_model_list_from_json(ESGenre, test_data_genre)


@pytest.fixture(scope='session')
def model_list_genre(model_list_genre_input) -> list[APIGenre]:
    """
        Список базовых конечных моделей для тестирования api. Т.к. имена полей
        отличаются во входной и выходной моделях, требуется конвертация.
        :param model_list_genre_input: Список входных моделей.
        """
    models = [
        APIGenre(
            uuid=genre.id,
            name=genre.name
        )
        for genre in model_list_genre_input
    ]
    return models


@pytest.fixture(scope='class')
async def provide_es_index_data_genre(settings: ConfTest,
                                      load_es_data,
                                      model_list_genre_input,
                                      clear_data_es_redis):
    await load_es_data(model_list_genre_input, index=settings.elastic_index_genre)
    yield
    await clear_data_es_redis(es_index_name=settings.elastic_index_genre)


@pytest.fixture(scope='session')
def exist_genre_id(model_list_genre: list[APIGenre]) -> UUID:
    return get_exist_index_id(model_list_genre)


@pytest.fixture(scope='session')
def exist_genre_model(model_list_genre, exist_genre_id) -> APIGenre:
    return get_model_by_id(model_list_genre, exist_genre_id)


@pytest.fixture(scope='session')
def get_model_list_genre(model_list_genre: list[APIGenre]):
    def inner(model_list: list[APIGenre]):
        ids = [model.uuid for model in model_list]
        models = [
            ESGenre(
                id=model.uuid,
                name=model.name,
                description=''
            )
            for model in model_list_genre if model.uuid in ids
        ]
        return models

    return inner


@pytest.fixture(scope='session')
def create_es_data_genre(settings: ConfTest,
                         model_list_genre_input: list[APIGenre],
                         exist_genre_id: UUID,
                         create_es_docs):
    async def inner(genre_ids: list[UUID] = None):
        if genre_ids:
            models = [
                get_es_model_by_id(model_list_genre_input, genre_id)
                for genre_id in genre_ids]
        else:
            models = get_es_model_by_id(model_list_genre_input, exist_genre_id)
        await create_es_docs(settings.elastic_index_genre, models)

    return inner


@pytest.fixture(scope='session')
def delete_es_data_genre(settings: ConfTest,
                         exist_genre_id: UUID,
                         delete_es_docs):
    async def inner(film_ids: list[str] = None):
        data = film_ids if film_ids else exist_genre_id
        await delete_es_docs(settings.elastic_index_genre, data)

    return inner


@pytest.fixture(scope='class')
def genre_list_parameters(model_list_genre: list[APIGenre]):
    genre_count = len(model_list_genre)
    params = [({}, DEFAULT_PAGE_SIZE)]
    params += get_page_parameters(genre_count)
    return params


@pytest.fixture(scope='class')
def genre_params_404(model_list_genre) -> dict:
    genres_count = len(model_list_genre)
    params = get_page_parameters_404(genres_count)
    return params


@pytest.fixture(scope='class')
def asset_genres(make_get_request,
                 get_model_list_genre,
                 assert_response_equal_base_models,
                 assert_status_len,
                 genre_sort_key):
    async def inner(query, parameters, page_size):
        response: HTTPResponse = await make_get_request(query, parameters)
        assert_status_len(response, page_size)

        response_models, ids = get_models_and_ids(response, APIGenre)
        base_models = get_model_list_genre(response_models)
        assert_response_equal_base_models(response_models, base_models,
                                          genre_sort_key)
        return ids

    return inner


@pytest.fixture(scope='class')
def asset_genre(assert_single_response,
                exist_genre_model: APIGenre):
    async def inner(query):
        await assert_single_response(query, APIGenre, exist_genre_model)

    return inner
