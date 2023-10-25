# noinspection SqlAggregates
filmwork_collect_query = """
SELECT
       fw.id,
       fw.title,
       fw.description,
       fw.rating,
       fw.type,
       fw.created,
       fw.modified,
       COALESCE (
           json_agg(
               DISTINCT jsonb_build_object(
                   'person_role', pfw.role,
                   'person_id', p.id,
                   'person_name', p.full_name
               )
           ) FILTER (WHERE p.id is not null),
           '[]'
       ) as persons,
       json_agg(
            DISTINCT jsonb_build_object(
                    'id', g.id,
                    'name', g.name)
            ) as genres
    FROM content.film_work fw
        LEFT JOIN content.person_film_work pfw ON pfw.film_work_id = fw.id
        LEFT JOIN content.person p ON p.id = pfw.person_id
        LEFT JOIN content.genre_film_work gfw ON gfw.film_work_id = fw.id
        LEFT JOIN content.genre g ON g.id = gfw.genre_id
    WHERE 
        fw.id IN %(ids)s
    GROUP BY fw.id
    ORDER BY fw.modified
"""

filmwork_filter_by_filmwork_dt = """
SELECT DISTINCT fw.id, fw.modified
FROM content.film_work fw
WHERE fw.modified > %(dt)s
"""

filmwork_filter_by_genre_dt = """
SELECT DISTINCT fw.id, g.modified
FROM content.film_work fw
LEFT JOIN content.genre_film_work gfw ON fw.id = gfw.film_work_id
LEFT JOIN content.genre g ON gfw.genre_id = g.id
WHERE g.modified > %(dt)s
"""

filmwork_filter_by_person_dt = """
SELECT DISTINCT fw.id, p.modified
FROM content.film_work fw
LEFT JOIN content.person_film_work pfw ON fw.id = pfw.film_work_id
LEFT JOIN content.person p ON pfw.person_id = p.id
WHERE p.modified > %(dt)s
"""

select_genres_by_update_dt = """
SELECT 
    g.id,
    g.modified
FROM 
    content.genre g
WHERE
    g.modified > %(dt)s
"""

genres_collect_query = """
SELECT 
    g.id,
    g.name,
    g.description,
    g.created,
    g.modified
FROM 
    content.genre g
WHERE
    g.id IN %(ids)s
"""

select_persons_by_update_dt = """
SELECT 
    p.id,
    p.modified
FROM content.person p
WHERE
    p.modified > %(dt)s
"""

person_collect_query = """
SELECT 
    p.id,
    p.full_name,
    p.created,
    p.modified,
    json_agg(jsonb_build_object(
                   'role', pfw.role,
                   'filmwork', pfw.film_work_id
               )) AS filmworks
FROM
    content.person p
    LEFT JOIN content.person_film_work pfw ON pfw.person_id = p.id
WHERE p.id IN %(ids)s
GROUP BY p.id
"""
