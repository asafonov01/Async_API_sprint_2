import json
import random
from pathlib import Path
from typing import TypeVar, Union
from uuid import UUID

from functional.models.response_model import HTTPResponse
from settings import MAX_PAGE_SIZE

OUT_MODEL = TypeVar('OUT_MODEL', bound='BaseModel')


def get_json_from_file(file: Path) -> json:
    with open(file, 'r') as f:
        data = json.load(f)
        return data


def get_model_list_from_json(model_in, test_data: json) -> list:
    return [model_in(**item) for item in test_data]


def get_exist_index_id(model_list) -> UUID:
    choise = random.choice(model_list)
    return choise.uuid


def get_model_by_id(model_list: list, model_id: UUID):
    for model in model_list:
        if str(model.uuid) == str(model_id):
            return model
    return None


def get_es_model_by_id(model_list: list, model_id: UUID):
    for model in model_list:
        if str(model.id) == str(model_id):
            return model
    return None


def get_id_count_in_model_field(model_list: list,
                                field: str, item_ids: Union[str, list]):
    if type(item_ids) is not list:
        item_ids = [item_ids, ]
    count = 0
    for model in model_list:
        for couple in model.dict()[f'{field}']:
            id_ = couple['uuid']
            if str(id_) in item_ids:
                count += 1
                break
    return count


def get_page_values(item_count: int):
    assert item_count > 0
    page_size = min(random.randint(1, item_count), MAX_PAGE_SIZE)
    filled_pages_count, remain = divmod(item_count, page_size)
    return filled_pages_count, remain, page_size


def get_page_parameters(item_count: int,
                        parameters: dict = None) -> list[tuple[dict, int]]:
    pages_count, remain, page_size = get_page_values(item_count)
    params = {} if parameters is None else parameters
    if item_count == 1:
        return [
            ({'page[size]': 1, 'page[number]': 1} | params, 1)
        ]
    if item_count == 2:
        return [
            ({'page[size]': 1, 'page[number]': 1} | params, 1),
            ({'page[size]': 1, 'page[number]': 2} | params, 1),
            ({'page[size]': 2, 'page[number]': 1} | params, 2),
        ]
    if remain:
        last_page_size = item_count - pages_count * page_size
        pages_count += 1
    else:
        last_page_size = page_size
    first_page_num = 1
    middle_page_num = (pages_count - 1) // 2 + 1
    final_page_num = pages_count
    result = [
        ({'page[size]': page_size, 'page[number]': first_page_num} | params,
         page_size),
        ({'page[size]': last_page_size, 'page[number]': final_page_num} | params,
         last_page_size),
    ]
    if middle_page_num != first_page_num:
        result += [
            ({'page[size]': page_size, 'page[number]': middle_page_num} | params,
             page_size),
        ]
    return result


def get_page_parameters_404(item_count: int,
                            parameters: dict = None) -> dict:
    params = {} if parameters is None else parameters
    filled_pages_count, remain, page_size = get_page_values(item_count)
    next_page_with_remain = filled_pages_count + 1
    return {'page[size]': page_size, 'page[number]': next_page_with_remain + 1} | params


def get_models_and_ids(response: HTTPResponse, required_model: OUT_MODEL):
    response_models, response_ids = [], []
    for item in response.body:
        model = required_model(**item)
        response_models.append(model)
        response_ids.append(model.uuid)
    return response_models, response_ids
