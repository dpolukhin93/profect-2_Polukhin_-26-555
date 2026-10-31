import json
import os

from primitive_db import decorators
from primitive_db.constants import DB_DATA_FOLDER


@decorators.handle_db_errors
def load_metadata(filepath: str) -> dict:
    """Читает метаданные из файла. 
    Если файл отсутствует - возвращает пустые метаданные."""

    if not os.path.exists(filepath):
        return {}

    with open(filepath, encoding="utf-8") as file:
            metadata = json.load(file)
            return metadata

        
@decorators.handle_db_errors
def save_metadata(filepath: str, data: dict) -> None:
    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


@decorators.handle_db_errors
def load_table_data(table_name: str) -> list[dict]:

    if not os.path.exists(DB_DATA_FOLDER):
        os.mkdir(DB_DATA_FOLDER)

    filepath = table_filepath(table_name)
    if not os.path.exists(filepath):
        return []
    
    with open(filepath) as file:
        table_data = json.load(file)
        return table_data


@decorators.handle_db_errors
def save_table_data(table_name: str, data: list[dict]) -> None:
    with open(table_filepath(table_name), "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


@decorators.handle_db_errors
def delete_table_file(table_name:str):
    os.remove(table_filepath(table_name))

    
def wrong_value_message(value_repr: str) -> str:
    return f"Некорректное значение: <{value_repr}>. Попробуйте снова."


def table_filepath(table_name):
    return os.path.join(DB_DATA_FOLDER, f"{table_name}.json")
