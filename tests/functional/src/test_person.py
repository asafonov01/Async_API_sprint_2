from http import HTTPStatus
from uuid import uuid4

import pytest

from functional.testdata.parameters.base_parameters import (
    BASE_PARAMETERS, PAGE_BAD_PARAMETERS, PAGE_PARAMETERS,
    PAGE_SORT_BAD_PARAMETERS, SORT_BAD_PARAMETERS, SORT_PARAMETERS)
from settings import ConfTest


class TestPersonWithoutData:

    @pytest.mark.parametrize(
        'query_parameters', [*BASE_PARAMETERS, *PAGE_PARAMETERS])
    @pytest.mark.asyncio
    async def test_person_list_404(self, make_get_request,
                                   settings,
                                   query_parameters):
        url = settings.person_list_url
        response = await make_get_request(url, query_parameters)
        assert len(response.body) == 0

    @pytest.mark.asyncio
    async def test_person_detail_404(self, make_get_request,
                                     settings,
                                     exist_person_id):
        url = settings.person_detail_url.format(exist_person_id)
        response = await make_get_request(url)
        assert response.status == HTTPStatus.NOT_FOUND

    @pytest.mark.parametrize(
        'query_parameters',
        [*BASE_PARAMETERS, *PAGE_PARAMETERS, *SORT_PARAMETERS])
    @pytest.mark.asyncio
    async def test_person_films_404(self, make_get_request,
                                    settings,
                                    exist_person_id,
                                    query_parameters):
        url = settings.person_films_url.format(exist_person_id)
        response = await make_get_request(url, query_parameters)
        assert len(response.body) == 0

    @pytest.mark.parametrize('query_parameters', [*PAGE_BAD_PARAMETERS])
    @pytest.mark.asyncio
    async def test_person_list_422(self, make_get_request,
                                   settings,
                                   query_parameters):
        url = settings.person_list_url
        response = await make_get_request(url, query_parameters)
        assert response.status == HTTPStatus.UNPROCESSABLE_ENTITY

    @pytest.mark.parametrize(
        'query_parameters', [*PAGE_BAD_PARAMETERS,
                             *SORT_BAD_PARAMETERS,
                             *PAGE_SORT_BAD_PARAMETERS])
    @pytest.mark.asyncio
    async def test_person_films_422(self, make_get_request,
                                    settings,
                                    exist_person_id,
                                    query_parameters):
        url = settings.person_films_url.format(exist_person_id)
        response = await make_get_request(url, query_parameters)
        assert response.status == HTTPStatus.UNPROCESSABLE_ENTITY


@pytest.mark.usefixtures(
    'provide_es_index_data_person', 'provide_es_index_data_movie')
class TestPerson:
    uuid_404 = uuid4()

    @pytest.mark.asyncio
    async def test_persons_cached(self, settings,
                                  person_list_parameters,
                                  assert_person_list,
                                  create_es_persons,
                                  delete_es_persons):
        url = settings.person_list_url
        for couple in person_list_parameters:
            parameters, page_size = couple
            ids = await assert_person_list(url, parameters, page_size)
            await delete_es_persons(ids)
            await assert_person_list(url, parameters, page_size)
            await create_es_persons(ids)

    @pytest.mark.asyncio
    async def test_person_detail_cached(self, exist_person_id,
                                        settings: ConfTest,
                                        assert_person_detail,
                                        create_es_persons,
                                        delete_es_persons):
        url = settings.person_detail_url.format(exist_person_id)
        await assert_person_detail(url)
        await delete_es_persons()
        await assert_person_detail(url)
        await create_es_persons()

    @pytest.mark.asyncio
    async def test_person_films_cached(self, exist_person_id,
                                       settings,
                                       assert_film_list,
                                       person_film_parameters,
                                       delete_es_film_data,
                                       create_es_film_data):
        url = settings.person_films_url.format(exist_person_id)
        for couple in person_film_parameters:
            parameters, page_size = couple
            ids = await assert_film_list(url, parameters, page_size)
            await delete_es_film_data(ids)
            await assert_film_list(url, parameters, page_size)
            await create_es_film_data(ids)

    @pytest.mark.asyncio
    async def test_person_404(self, make_get_request,
                              settings):
        url = settings.person_detail_url.format(self.uuid_404)
        response = await make_get_request(url)
        assert response.status == HTTPStatus.NOT_FOUND

    @pytest.mark.asyncio
    async def test_person_films_404(self, make_get_request,
                                    settings,
                                    exist_person_id,
                                    person_film_params_404):
        url = settings.person_films_url.format(self.uuid_404)
        response = await make_get_request(url)
        assert len(response.body) == 0

        for parameters in person_film_params_404:
            url = settings.person_films_url.format(exist_person_id)
            response = await make_get_request(url, parameters)
            assert len(response.body) == 0

    @pytest.mark.asyncio
    async def test_person_list_404(self, make_get_request,
                                   settings: ConfTest,
                                   person_list_params_404):
        url = settings.person_list_url
        response = await make_get_request(url, person_list_params_404)
        assert len(response.body) == 0

    @pytest.mark.parametrize('query_parameters', [*PAGE_BAD_PARAMETERS])
    @pytest.mark.asyncio
    async def test_person_list_422(self, make_get_request,
                                   settings,
                                   query_parameters):
        url = settings.person_list_url
        response = await make_get_request(url, query_parameters)
        assert response.status == HTTPStatus.UNPROCESSABLE_ENTITY

    @pytest.mark.parametrize('query_parameters',
                             [*PAGE_BAD_PARAMETERS,
                              *SORT_BAD_PARAMETERS,
                              *PAGE_SORT_BAD_PARAMETERS])
    @pytest.mark.asyncio
    async def test_person_films_422(self, make_get_request,
                                    settings,
                                    exist_person_id,
                                    query_parameters):
        url = settings.person_films_url.format(exist_person_id)
        response = await make_get_request(url, query_parameters)
        assert response.status == HTTPStatus.UNPROCESSABLE_ENTITY
