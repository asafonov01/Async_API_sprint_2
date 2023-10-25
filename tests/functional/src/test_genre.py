from http import HTTPStatus
from uuid import UUID, uuid4

import pytest

from functional.testdata.parameters.base_parameters import (PAGE_BAD_PARAMETERS,
                                                            PAGE_PARAMETERS)
from settings import ConfTest


class TestGenreWithoutData:
    uuid_404 = uuid4()

    @pytest.mark.asyncio
    async def test_genre_detail_404(self, settings: ConfTest,
                                    make_get_request):
        url = settings.genre_detail_url.format(self.uuid_404)
        response = await make_get_request(url)
        assert response.status == HTTPStatus.NOT_FOUND

    @pytest.mark.parametrize(
        'query_parameters', [*PAGE_PARAMETERS])
    @pytest.mark.asyncio
    async def test_genre_list_404(self, settings: ConfTest,
                                  make_get_request,
                                  query_parameters: dict):
        url = settings.genre_list_url
        response = await make_get_request(url)
        assert len(response.body) == 0

    @pytest.mark.parametrize(
        'query_parameters', [*PAGE_BAD_PARAMETERS])
    async def test_genre_list_422(self, settings: ConfTest,
                                  make_get_request,
                                  query_parameters: dict):
        url = settings.genre_list_url
        response = await make_get_request(url, query_parameters)
        assert response.status == HTTPStatus.UNPROCESSABLE_ENTITY


@pytest.mark.usefixtures('provide_es_index_data_genre')
class TestGenre:
    uuid_404 = uuid4()

    @pytest.mark.asyncio
    async def test_genre_list_cached(self, settings: ConfTest,
                                     genre_list_parameters,
                                     asset_genres,
                                     delete_es_data_genre,
                                     create_es_data_genre):
        url = settings.genre_list_url
        for couple in genre_list_parameters:
            parameters, page_size = couple
            genre_ids = await asset_genres(url, parameters, page_size)
            await delete_es_data_genre(genre_ids)
            await asset_genres(url, parameters, page_size)
            await create_es_data_genre(genre_ids)

    @pytest.mark.asyncio
    async def test_genre_detail_cached(self, settings: ConfTest,
                                       exist_genre_id: UUID,
                                       asset_genre,
                                       delete_es_data_genre,
                                       create_es_data_genre):
        url = settings.genre_detail_url.format(exist_genre_id)
        await asset_genre(url)
        await delete_es_data_genre()
        await asset_genre(url)
        await create_es_data_genre()

    @pytest.mark.asyncio
    async def test_genre_detail_404(self, make_get_request,
                                    settings: ConfTest):
        url = settings.genre_detail_url.format(self.uuid_404)
        response = await make_get_request(url)
        assert response.status == HTTPStatus.NOT_FOUND

    @pytest.mark.asyncio
    async def test_genre_list_404(self, make_get_request,
                                  settings: ConfTest,
                                  genre_params_404: dict):
        url = settings.genre_list_url
        response = await make_get_request(url, genre_params_404)
        assert len(response.body) == 0

    @pytest.mark.parametrize(
        'query_parameters', [*PAGE_BAD_PARAMETERS])
    async def test_genre_list_422(self, make_get_request,
                                  settings: ConfTest,
                                  query_parameters: dict):
        url = settings.genre_list_url
        response = await make_get_request(url, query_parameters)
        assert response.status == HTTPStatus.UNPROCESSABLE_ENTITY
