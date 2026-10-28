from primitive_db import utils
from primitive_db.constants import AVAILABLE_TYPES, ID_COLUMN


def create_table(metadata:dict, table_name:str, columns:list[dict]):
    
    if table_name in metadata:
        raise ValueError(f"Ошибка: Таблица \"{table_name}\" уже существует!")

    errors = []
    need_id = True
    id_index = 0
    for i, column in enumerate(columns):
        if column["name"] == ID_COLUMN["name"]:
            need_id = False
            id_index = i
            if column["type"] != ID_COLUMN["type"]:
                value_repr = f'{column["name"]}:{column["type"]}'
                errors.append(utils.wrong_value_message(value_repr))
                continue

        if column["type"] not in AVAILABLE_TYPES:
            value_repr = f'{column["name"]}:{column["type"]}'
            errors.append(utils.wrong_value_message(value_repr))

    if errors:
        raise ValueError("\n".join(error for error in errors))

    if need_id:
        columns.insert(0, ID_COLUMN.copy())
    else:
        columns.insert(0, columns.pop(id_index))

    metadata[table_name] = columns

    return metadata

def drop_table(metadata:dict, table_name:str) -> dict:
    
    if table_name not in metadata:
        raise ValueError(f"Ошибка: Таблица \"{table_name}\" не существует!")

    metadata.pop(table_name)

    return metadata

def print_list_of_tables(metadata:dict) -> None:
    
    for key in metadata:
        print(f"- {key}")