class ESQueryParameters:
    @staticmethod
    def get_es_sorting(sort_field_string: str) -> list:
        """Метод для получения параметров сотрировки в запросе к ES"""
        sorting = []
        if sort_field_string[0] == "-":
            sorting.append({sort_field_string[1:]: "desc"})
            return sorting
        sorting.append({sort_field_string: "asc"})
        return sorting

    @staticmethod
    def get_es_pagination_parameters(p_size: int, p_number: int) -> dict:
        """Метод для получения параметров пагинации для запроса в ES"""
        params_dict = {"from": 0, "size": p_size}
        p_number -= 1
        params_dict["from"] = p_size * p_number
        return params_dict
