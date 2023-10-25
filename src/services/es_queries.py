# services/films.py queries
FILMS_QUERY = {
    "query": {"match_all": {}},
    "_source": ["id", "title", "imdb_rating"],
}
GENRE_FILTERED_FILMS_QUERY = {
    "query": {
        "nested": {
            "path": "genre",
            "query": {
                "match": {},
            },
        },
    },
    "_source": ["id", "title", "imdb_rating"],
}
FILMS_SEARCH_QUERY = {
    "query": {
        "multi_match": {
            "query": None,
            "fields": [
                "title",
                "description",
            ],
        }
    },
    "_source": ["id", "title", "imdb_rating"],
}

# services/genres.py queries
GENRES_QUERY = {
    "query": {"match_all": {}},
    "_source": ["id", "name"],
}

# services/persons.py queries
PERSONS_SEARCH_QUERY = {
    "query": {
        "match": {
            "name": {
                "query": None,
            },
        }
    }
}

PERSONS_QUERY = {
    "query": {"match_all": {}},
    "_source": ["id", "name"],
}
