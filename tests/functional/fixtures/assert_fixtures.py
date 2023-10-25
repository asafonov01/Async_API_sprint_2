from typing import Callable

import pytest

from functional.models.response_model import HTTPResponse


@pytest.fixture(scope='session')
def film_sort_key() -> Callable:
    return lambda x: (x.title, x.imdb_rating)


@pytest.fixture(scope='session')
def person_sort_key() -> Callable:
    return lambda x: x.full_name


@pytest.fixture(scope='session')
def genre_sort_key() -> Callable:
    return lambda x: x.name


@pytest.fixture(scope='session')
def assert_response_equal_base_models():
    """Сравнение полученных от fastapi моделей с исходными"""

    def inner(response_models, base_models, sort_key):
        assert response_models.sort(
            key=sort_key) == base_models.sort(key=sort_key)

    return inner


@pytest.fixture(scope='session')
def assert_film_list_sort_valid():
    def inner(models, parameters):
        order = parameters.get('sort') != 'imdb_rating'
        for i, model in enumerate(models):
            if i:
                if order:
                    assert model.imdb_rating <= models[i - 1].imdb_rating
                else:
                    assert model.imdb_rating >= models[i - 1].imdb_rating

    return inner


@pytest.fixture(scope='session')
def assert_status_len():
    def inner(response: HTTPResponse, page_size: int):
        assert response.status == 200
        assert len(response.body) == page_size

    return inner


@pytest.fixture(scope='session')
def assert_single_response(make_get_request):
    async def inner(query: str, model, exist_model):
        response: HTTPResponse = await make_get_request(query)
        assert response.status == 200
        response_model = model(**response.body)
        assert response_model == exist_model

    return inner
