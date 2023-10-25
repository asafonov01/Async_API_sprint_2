import uuid

random_uuid = str(uuid.uuid4())

FILTER_GENRE_PARAMS = [{'filter[genre]': random_uuid}, ]

FILM_ALL_PARAMETERS = [
    {'sort': '-imdb_rating', 'filter[genre]': random_uuid,
     'page[size]': 5, 'page[number]': 20},
    {'sort': 'imdb_rating', 'filter[genre]': random_uuid,
     'page[size]': 5, 'page[number]': 20}
]

FILM_ALL_BAD_PARAMETERS = [
    {'sort': '-anyfield', 'filter[genre]': random_uuid,
     'page[size]': 5, 'page[number]': 20},
    {'sort': 'imdb_rating', 'filter[genre]': random_uuid,
     'page[size]': -5, 'page[number]': 20},
    {'sort': 'imdb_rating', 'filter[genre]': random_uuid,
     'page[size]': 5, 'page[number]': -20},
]
