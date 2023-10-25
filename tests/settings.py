from pathlib import Path

from pydantic import BaseSettings

BASE_DIR = Path(__file__).resolve(strict=True).parent

ES_PAGE_MAX_SIZE = 10000  # Максимальный размер страницы результатов
DEFAULT_PAGE_SIZE = 10  # Размер списка выдачи по умолчанию
MAX_PAGE_SIZE = 500  # Максимальный размер страницы для тестирования


class ConfTest(BaseSettings):
    redis_host: str = 'localhost'
    redis_port: int = 6379
    elastic_host: str = 'localhost'
    elastic_port: int = 9200
    elastic_user: str = 'elastic'
    elastic_scheme: str = 'http'
    elastic_index_film: str = 'movies'
    movie_path: Path = BASE_DIR / 'functional/testdata/movies.json'
    elastic_index_genre: str = 'genres'
    genre_path = BASE_DIR / 'functional/testdata/genres.json'
    elastic_index_person: str = 'persons'
    person_path = BASE_DIR / 'functional/testdata/persons.json'
    service_host: str = 'localhost'
    service_port: str = 8000
    service_scheme: str = 'http'
    api_version: str = 'v1'

    # class Config:
    #     env_file = '.env'

    @property
    def service_url(self):
        return (f'{self.service_scheme}://{self.service_host}:{self.service_port}/api/'
                f'{self.api_version}')

    @property
    def person_search_url(self):
        return self.service_url + '/persons/search'

    @property
    def film_search_url(self):
        return self.service_url + '/films/search'

    @property
    def genre_detail_url(self):
        return self.service_url + '/genres/{0}'

    @property
    def genre_list_url(self):
        return self.service_url + '/genres'

    @property
    def person_detail_url(self):
        return self.service_url + '/persons/{0}'

    @property
    def person_list_url(self):
        return self.service_url + '/persons'

    @property
    def person_films_url(self):
        return self.service_url + '/persons/{0}/films'

    @property
    def film_detail_url(self):
        return self.service_url + '/films/{0}'

    @property
    def film_list_url(self):
        return self.service_url + '/films'
