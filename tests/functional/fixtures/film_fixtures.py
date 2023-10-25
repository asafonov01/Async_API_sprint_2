import json
import uuid
from uuid import UUID

import pytest

from functional.models.api_models import APIFilmFull, APIFilmShort
from functional.models.es_models import ESFilm
from functional.models.response_model import HTTPResponse
from functional.utils.auxiliary import (get_json_from_file, get_model_list_from_json,
                                        get_model_by_id, get_exist_index_id,
                                        get_id_count_in_model_field,
                                        get_page_parameters, get_page_parameters_404, get_models_and_ids,
                                        get_es_model_by_id)
from settings import ConfTest, DEFAULT_PAGE_SIZE


@pytest.fixture(scope='session')
def test_data_movie(settings: ConfTest) -> json:
    return get_json_from_file(settings.movie_path)


@pytest.fixture(scope='session')
def model_list_movie_input(test_data_movie: json) -> list[ESFilm]:
    """
    Список базовых входных моделей, получаемый из тестового файла.
    Используется для загрузки в данных в Elasticsearch при тестировании кэша
    (когда требуется удалять и записывать часть данных, а не все).
    :param test_data_movie: Файл с тестовыми данными.
    """
    return get_model_list_from_json(ESFilm, test_data_movie)


@pytest.fixture(scope='session')
def model_list_movie(
        model_list_movie_input: list[ESFilm]) -> list[APIFilmFull]:
    """
    Список базовых конечных моделей для тестирования api. Т.к. имена полей
    отличаются во входной и выходной моделях, требуется конвертация.
    :param model_list_movie_input: Список входных моделей.
    """
    models = [
        APIFilmFull(
            uuid=film.id,
            title=film.title,
            imdb_rating=film.imdb_rating or 0.0,
            description=film.description,
            genre=[{"uuid": genre.id, "name": genre.name}
                   for genre in film.genre],
            actors=[{"uuid": actor.id, "full_name": actor.name}
                    for actor in film.actors],
            writers=[{"uuid": writer.id, "full_name": writer.name}
                     for writer in film.writers],
            directors=[{"uuid": director.id, "full_name": director.name}
                       for director in film.directors],
        ) for film in model_list_movie_input]
    return models


@pytest.fixture(scope='session')
def get_model_list_movie_short(model_list_movie: list[APIFilmFull]):
    """
    Предоставляет модели для тестирования списков фильмов.
    """

    def inner(model_list: list[APIFilmShort]) -> list[APIFilmShort]:
        ids = [model.uuid for model in model_list]
        models = [APIFilmShort(
            uuid=model.uuid, title=model.title, imdb_rating=model.imdb_rating
        ) for model in model_list_movie if model.uuid in ids]
        return models

    return inner


@pytest.fixture(scope='class')
async def provide_es_index_data_movie(settings: ConfTest,
                                      load_es_data,
                                      model_list_movie_input: list[ESFilm],
                                      clear_data_es_redis):
    """
    Предоставляет данные для тестирования в Elasticsearch.
    После тестирования данные удаляются из redis и Elasticsearch.
    """
    await load_es_data(model_list_movie_input, settings.elastic_index_film)
    yield
    await clear_data_es_redis(settings.elastic_index_film)


@pytest.fixture(scope='session')
def create_es_film_data(settings: ConfTest,
                        model_list_movie_input: list[APIFilmShort],
                        exist_film_id: UUID,
                        create_es_docs):
    async def inner(film_ids: list[UUID] = None):
        """
        Записывает в Elasticsearch фильм или список фильмов.
        """
        if film_ids:
            models = [
                get_es_model_by_id(model_list_movie_input, film_id)
                for film_id in film_ids]
        else:
            models = get_es_model_by_id(model_list_movie_input, exist_film_id)
        await create_es_docs(settings.elastic_index_film, models)

    return inner


@pytest.fixture(scope='session')
def delete_es_film_data(settings: ConfTest,
                        exist_film_id: UUID,
                        delete_es_docs):
    """
    Удаляет из elasticsearch фильм - если фикстура вызывается без параметров,
    иначе удаляет список фильмов.
    """

    async def inner(film_ids: list[str] = None):
        data = film_ids if film_ids else exist_film_id
        await delete_es_docs(settings.elastic_index_film, data)

    return inner


@pytest.fixture(scope='session')
def exist_film_id(model_list_movie: list[APIFilmFull]) -> UUID:
    return get_exist_index_id(model_list_movie)


@pytest.fixture(scope='session')
def exist_film_model(model_list_movie, exist_film_id) -> APIFilmFull:
    return get_model_by_id(model_list_movie, exist_film_id)


@pytest.fixture(scope='class')
def film_list_params(model_list_movie,
                     exist_film_id) -> list[tuple[dict, int]]:
    film_model: APIFilmFull = get_model_by_id(model_list_movie, exist_film_id)
    film_count = len(model_list_movie)
    assert len(film_model.genre) > 0
    genre_id = str(film_model.genre[0].uuid)
    count_by_genre = get_id_count_in_model_field(
        model_list_movie, 'genre', genre_id)

    params = [
        ({}, DEFAULT_PAGE_SIZE),
        ({'sort': 'imdb_rating'}, DEFAULT_PAGE_SIZE),
        ({'sort': '-imdb_rating'}, DEFAULT_PAGE_SIZE),
        ({'filter[genre]': genre_id}, min(count_by_genre, DEFAULT_PAGE_SIZE))
    ]
    params += get_page_parameters(
        count_by_genre, {'sort': '-imdb_rating', 'filter[genre]': genre_id})
    params += get_page_parameters(
        count_by_genre, {'sort': 'imdb_rating', 'filter[genre]': genre_id})
    params += get_page_parameters(film_count)
    params += get_page_parameters(film_count, {'sort': 'imdb_rating'})
    params += get_page_parameters(film_count, {'sort': '-imdb_rating'})
    return params


@pytest.fixture(scope='class')
def film_list_params_404(model_list_movie) -> list[dict]:
    non_exist_genre_id = str(uuid.uuid4())
    films_count = len(model_list_movie)
    params = [
        {'filter[genre]': non_exist_genre_id},
        get_page_parameters_404(films_count),
        get_page_parameters_404(films_count, {'sort': 'imdb_rating'}),
        get_page_parameters_404(films_count, {'sort': '-imdb_rating'})
    ]
    return params


@pytest.fixture(scope='class')
def assert_film_list(make_get_request,
                     get_model_list_movie_short,
                     assert_film_list_sort_valid,
                     assert_response_equal_base_models,
                     assert_status_len,
                     film_sort_key):
    async def inner(query, parameters, page_size) -> list[UUID]:
        response: HTTPResponse = await make_get_request(query, parameters)
        assert_status_len(response, page_size)

        response_models, ids = get_models_and_ids(response, APIFilmShort)
        assert_film_list_sort_valid(response_models, parameters)

        base_models = get_model_list_movie_short(response_models)
        assert_response_equal_base_models(
            response_models, base_models, film_sort_key)
        return ids

    return inner


@pytest.fixture(scope='class')
def assert_film_detail(assert_single_response,
                       exist_film_model):
    async def inner(query):
        await assert_single_response(query, APIFilmFull, exist_film_model)

    return inner
