BASE_PARAMETERS = [{}, ]

PAGE_PARAMETERS = [
    {'page[number]': 1},
    {'page[size]': 5},
    {'page[size]': 5, 'page[number]': 1},
    {'page[size]': 15, 'page[number]': 5},
    {'page[size]': 10, 'page[number]': 99},
]

PAGE_BAD_PARAMETERS = [
    {'page[number]': -1},
    {'page[number]': -20},
    {'page[size]': 'text'},
    {'page[number]': 'text'},
    {'page[size]': -1, 'page[number]': 20},
    {'page[size]': 5, 'page[number]': -10},
    {'page[size]': -12, 'page[number]': -150},
    {'page[size]': -12, 'page[number]': 'text'},
    {'page[size]': 'text', 'page[number]': -150},
]

SORT_PARAMETERS = [
    {'sort': 'imdb_rating'},
    {'sort': '-imdb_rating'},
]

SORT_BAD_PARAMETERS = [
    {'sort': 'anyfield'},
    {'sort': '-anyfield'},
]

PAGE_SORT_BAD_PARAMETERS = [
    param | SORT_BAD_PARAMETERS[0] if i % 2 == 0
    else param | SORT_BAD_PARAMETERS[1]
    for i, param in enumerate(PAGE_BAD_PARAMETERS)]
