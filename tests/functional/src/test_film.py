from http import HTTPStatus
from uuid import UUID, uuid4

import pytest

from functional.models.response_model import HTTPResponse
from functional.testdata.parameters.base_parameters import (BASE_PARAMETERS,
                                                            SORT_PARAMETERS,
                                                            PAGE_PARAMETERS,
                                                            PAGE_BAD_PARAMETERS,
                                                            SORT_BAD_PARAMETERS,
                                                            PAGE_SORT_BAD_PARAMETERS)
from functional.testdata.parameters.film_parameters import (FILTER_GENRE_PARAMS,
                                                            FILM_ALL_PARAMETERS,
                                                            FILM_ALL_BAD_PARAMETERS)
from settings import ConfTest


class TestFilmWithoutData:

    @pytest.mark.parametrize(
        'query_parameters', [
            *BASE_PARAMETERS, *SORT_PARAMETERS, *PAGE_PARAMETERS,
            *FILTER_GENRE_PARAMS, *FILM_ALL_PARAMETERS
        ]
    )
    @pytest.mark.asyncio
    async def test_film_list(self, make_get_request,
                             settings: ConfTest,
                             query_parameters: dict):
        url = settings.film_list_url
        response: HTTPResponse = await make_get_request(url, query_parameters)
        assert response.status == HTTPStatus.OK
        assert len(response.body) == 0

    @pytest.mark.asyncio
    async def test_film_detail_404(self, make_get_request,
                                   settings: ConfTest,
                                   exist_film_id: UUID):
        url = settings.film_detail_url.format(exist_film_id)
        response = await make_get_request(url)
        assert response.status == HTTPStatus.NOT_FOUND

    @pytest.mark.parametrize(
        'query_parameters', [
            *PAGE_BAD_PARAMETERS,
            *SORT_BAD_PARAMETERS,
            *FILM_ALL_BAD_PARAMETERS
        ])
    @pytest.mark.asyncio
    async def test_film_list_422(self, make_get_request,
                                 settings: ConfTest,
                                 query_parameters: dict):
        url = settings.film_list_url
        response = await make_get_request(url, query_parameters)
        assert response.status == HTTPStatus.UNPROCESSABLE_ENTITY


@pytest.mark.usefixtures('provide_es_index_data_movie')
class TestFilm:
    uuid_404 = uuid4()

    @pytest.mark.asyncio
    async def test_film_list_cashed(self,
                                    settings,
                                    assert_film_list,
                                    film_list_params,
                                    create_es_film_data,
                                    delete_es_film_data):
        url = settings.film_list_url
        for item in film_list_params:
            parameters, page_size = item
            film_ids = await assert_film_list(url, parameters, page_size)
            await delete_es_film_data(film_ids)
            await assert_film_list(url, parameters, page_size)
            await create_es_film_data(film_ids)

    @pytest.mark.asyncio
    async def test_film_detail_cashed(self, settings: ConfTest,
                                      assert_film_detail,
                                      exist_film_id: UUID,
                                      create_es_film_data,
                                      delete_es_film_data):
        url = settings.film_detail_url.format(exist_film_id)
        await assert_film_detail(url)
        await delete_es_film_data()
        await assert_film_detail(url)
        await create_es_film_data()

    @pytest.mark.asyncio
    async def test_film_detail_404(self, make_get_request,
                                   settings: ConfTest):
        url = settings.film_detail_url.format(self.uuid_404)
        response: HTTPResponse = await make_get_request(url)
        assert response.status == HTTPStatus.NOT_FOUND

    @pytest.mark.asyncio
    async def test_film_list_404(self,
                                 film_list_params_404,
                                 settings: ConfTest,
                                 make_get_request
                                 ):
        url = settings.film_list_url
        for parameter in film_list_params_404:
            response: HTTPResponse = await make_get_request(url, parameter)
            assert len(response.body) == 0

    @pytest.mark.parametrize(
        'query_parameters', [*SORT_BAD_PARAMETERS,
                             *PAGE_BAD_PARAMETERS,
                             *PAGE_SORT_BAD_PARAMETERS,
                             *FILM_ALL_BAD_PARAMETERS])
    @pytest.mark.asyncio
    async def test_film_list_422(self, query_parameters: dict,
                                 settings: ConfTest,
                                 make_get_request):
        url = settings.film_list_url
        response: HTTPResponse = await make_get_request(url, query_parameters)
        assert response.status == HTTPStatus.UNPROCESSABLE_ENTITY
