import json
import logging
from functools import wraps
from time import sleep


def backoff(start_sleep_time=0.1, factor=2, border_sleep_time=10, logger=None):
    """
    Функция для повторного выполнения функции через некоторое время, если возникла ошибка.
    Использует наивный экспоненциальный рост времени повтора (factor) до граничного времени ожидания (border_sleep_time)

    Формула:
        t = start_sleep_time * 2^(n) if t < border_sleep_time
        t = border_sleep_time if t >= border_sleep_time
    :param start_sleep_time: начальное время повтора
    :param factor: во сколько раз нужно увеличить время ожидания
    :param border_sleep_time: граничное время ожидания
    :param logger: Специфичный вывод сообщений
    :return: результат выполнения функции
    """

    def func_wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            current_sleep_time = start_sleep_time
            while True:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if current_sleep_time >= border_sleep_time:
                        current_sleep_time = border_sleep_time
                    else:
                        current_sleep_time *= factor

                    sleep(current_sleep_time)

                    if logger:
                        logger.warning(msg=f"Exception during backoff, {str(e)}\n"
                                           f"Waiting for {current_sleep_time} seconds before next try...")

        return inner

    return func_wrapper


def open_file(path: str) -> str:
    with open(path) as f:
        return f.read()


def load_json_from_file(path: str) -> dict:
    return json.loads(open_file(path))


def get_logger(name: str):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger
