import json

from primitive_db.constants import DB_DATA_FOLDER


def load_metadata(filepath: str) -> dict:
    try:
        with open(filepath, encoding="utf-8") as file:
            metadata = json.load(file)
            return metadata
    except FileNotFoundError:
        return {}


def save_metadata(filepath: str, data: dict) -> None:
    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def load_table_data(table_name: str) -> list[dict]:
    try:
        with open(table_filepath(table_name)) as file:
            table_data = json.load(file)
            return table_data
    except FileNotFoundError:
        return []


def save_table_data(table_name: str, data: list[dict]) -> None:
    with open(table_filepath(table_name), "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def wrong_value_message(value_repr: str) -> str:
    return f"Некорректное значение: <{value_repr}>. Попробуйте снова."


def table_filepath(table_name):
    return f"{DB_DATA_FOLDER}\\{table_name}.json"


def table_not_found_error(table_name):
    return f'Ошибка: Таблица "{table_name}" не существует!'
