#!/bin/bash

status_code_movie=$(curl --write-out %\{http_code\} --silent --output -XGET -H 'Content-Type:application/json' "${ELASTIC_HOST}":"${ELASTIC_PORT}"/"${ELASTIC_INDEX_FILM}")
status_code_genre=$(curl --write-out %\{http_code\} --silent --output -XGET -H 'Content-Type:application/json' "${ELASTIC_HOST}":"${ELASTIC_PORT}"/"${ELASTIC_INDEX_GENRE}")
status_code_person=$(curl --write-out %\{http_code\} --silent --output -XGET -H 'Content-Type:application/json' "${ELASTIC_HOST}":"${ELASTIC_PORT}"/"${ELASTIC_INDEX_PERSON}")
if [ "$status_code_movie" -ne 200 ]
 then
  curl -XPUT -H 'Content-Type:application/json' --data-binary "@/home/curl_user/movies.json" "${ELASTIC_HOST}":"${ELASTIC_PORT}"/"${ELASTIC_INDEX_FILM}"
else echo "scheme ${ELASTIC_INDEX_FILM} exists"
fi
if [ "$status_code_genre" -ne 200 ]
 then
  curl -XPUT -H 'Content-Type:application/json' --data-binary "@/home/curl_user/genres.json" "${ELASTIC_HOST}":"${ELASTIC_PORT}"/"${ELASTIC_INDEX_GENRE}"
else echo "scheme ${ELASTIC_INDEX_GENRE} exists"
fi
if [ "$status_code_person" -ne 200 ]
 then
  curl -XPUT -H 'Content-Type:application/json' --data-binary "@/home/curl_user/schemas_person.json" "${ELASTIC_HOST}":"${ELASTIC_PORT}"/"${ELASTIC_INDEX_PERSON}"
else echo "scheme ${ELASTIC_INDEX_PERSON} exists"
fi
exit 0