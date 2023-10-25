import uuid
from http import HTTPStatus

import pytest

from functional.models.api_models import APIFilmFull
from functional.models.api_models import APIPersonFull
from functional.testdata.parameters.base_parameters import PAGE_BAD_PARAMETERS
from settings import ConfTest


class TestSearchWithoutData:
    @pytest.mark.asyncio
    async def test_search_film_404(self, make_get_request,
                                   settings: ConfTest):
        parameters = {'query': str(uuid.uuid4())}
        url = settings.film_search_url
        response = await make_get_request(url, parameters)
        assert len(response.body) == 0

    @pytest.mark.asyncio
    async def test_person_404(self, make_get_request,
                              settings: ConfTest):
        parameters = {'query': str(uuid.uuid4())}
        url = settings.person_search_url
        response = await make_get_request(url, parameters)
        assert len(response.body) == 0

    @pytest.mark.parametrize('query_parameters', [*PAGE_BAD_PARAMETERS])
    @pytest.mark.asyncio
    async def test_search_film_422(self, make_get_request,
                                   settings: ConfTest,
                                   exist_film_model: APIFilmFull,
                                   query_parameters: dict):
        parameters = {'query': exist_film_model.title} | query_parameters
        url = settings.film_search_url
        response = await make_get_request(url, parameters)
        assert response.status == HTTPStatus.UNPROCESSABLE_ENTITY

    @pytest.mark.parametrize('query_parameters', [*PAGE_BAD_PARAMETERS])
    @pytest.mark.asyncio
    async def test_search_person_422(self, make_get_request,
                                     settings: ConfTest,
                                     exist_person_model: APIPersonFull,
                                     query_parameters: dict):
        parameters = {'query': exist_person_model.full_name} | query_parameters
        url = settings.person_search_url
        response = await make_get_request(url, parameters)
        assert response.status == HTTPStatus.UNPROCESSABLE_ENTITY


@pytest.mark.usefixtures(
    'provide_es_index_data_person', 'provide_es_index_data_movie',
    'exist_person_id', 'settings')
class TestSearch:
    params_404 = {'query': str(uuid.uuid4())}

    @pytest.mark.asyncio
    async def test_search_film_cached(self, assert_search_film,
                                      exist_film_model: APIFilmFull,
                                      delete_es_film_data,
                                      film_search_params: dict,
                                      settings: ConfTest,
                                      create_es_film_data):
        url = settings.film_search_url
        for couple in film_search_params:
            page_params, page_size = couple
            parameters = {'query': exist_film_model.title} | page_params
            film_ids = await assert_search_film(url, parameters, page_size)
            await delete_es_film_data(film_ids)
            await assert_search_film(url, parameters, page_size)
            await create_es_film_data(film_ids)

    @pytest.mark.asyncio
    async def test_search_person_cached(self, exist_person_model: APIPersonFull,
                                        settings: ConfTest,
                                        delete_es_persons,
                                        create_es_persons,
                                        assert_search_person,
                                        person_search_params: dict):
        url = settings.person_search_url
        for couple in person_search_params:
            page_params, page_size = couple
            parameters = {'query': exist_person_model.full_name} | page_params

            person_ids = await assert_search_person(url, parameters, page_size)
            await delete_es_persons(person_ids)
            await assert_search_person(url, parameters, page_size)
            await create_es_persons(person_ids)

    @pytest.mark.asyncio
    async def test_search_film_404(self, make_get_request,
                                   settings: ConfTest,
                                   exist_film_model: APIFilmFull,
                                   film_search_params_404: dict):
        url = settings.film_search_url
        response = await make_get_request(url, self.params_404)
        assert len(response.body) == 0

        parameters = {'query': exist_film_model.title} | film_search_params_404
        response = await make_get_request(url, parameters)
        assert len(response.body) == 0

    @pytest.mark.asyncio
    async def test_search_person_404(self, make_get_request,
                                     settings: ConfTest,
                                     exist_person_model: APIPersonFull,
                                     person_search_params_404):
        url = settings.person_search_url
        response = await make_get_request(url, self.params_404)
        assert len(response.body) == 0

        parameters = {'query': exist_person_model.full_name} | person_search_params_404
        response = await make_get_request(url, parameters)
        assert len(response.body) == 0

    @pytest.mark.parametrize('query_parameters', [*PAGE_BAD_PARAMETERS])
    @pytest.mark.asyncio
    async def test_search_film_422(self, make_get_request,
                                   settings: ConfTest,
                                   exist_film_model: APIFilmFull,
                                   query_parameters: dict):
        parameters = {'query': exist_film_model.title} | query_parameters
        url = settings.film_search_url
        response = await make_get_request(url, parameters)
        assert response.status == HTTPStatus.UNPROCESSABLE_ENTITY

    @pytest.mark.parametrize('query_parameters', [*PAGE_BAD_PARAMETERS])
    @pytest.mark.asyncio
    async def test_search_person_422(self, make_get_request,
                                     settings: ConfTest,
                                     exist_person_model: APIPersonFull,
                                     query_parameters: dict):
        parameters = {'query': exist_person_model.full_name} | query_parameters
        url = settings.person_search_url
        response = await make_get_request(url, parameters)
        assert response.status == HTTPStatus.UNPROCESSABLE_ENTITY
