import os

import dotenv

from lib.utilites import get_logger

dotenv.load_dotenv()

logger = get_logger(__name__)

REDIS_KEY = os.environ.get('REDIS_STATE_KEY', 'etl_state')
CLEAN_ELASTIC_ON_START = os.environ.get('CLEAN_ELASTIC_ON_START', 'False').lower() == 'true'
CLEAN_REDIS_ON_START = os.environ.get('CLEAN_REDIS_ON_START', 'False').lower() == 'true'

DB_CHUNK_SIZE = int(os.environ.get('DB_CHUNK_SIZE', 100))
COLLECT_WAIT_TIME = 5

PG_CONN = {
    'dbname': os.environ.get('DB_NAME'),
    'user': os.environ.get('DB_USER'),
    'password': os.environ.get('DB_PASSWORD'),
    'host': os.environ.get('DB_HOST', '127.0.0.1'),
    'port': os.environ.get('DB_PORT', 5432)
}

ES_HOST = {
    'host': os.environ.get('ELASTIC_HOST'),
    'port': int(os.environ.get('ELASTIC_PORT')),
    'scheme': os.environ.get('ELASTIC_SCHEME', 'http')
}

REDIS_CONN = {
    'host': os.environ.get('REDIS_HOST'),
    'port': os.environ.get('REDIS_PORT')
}
