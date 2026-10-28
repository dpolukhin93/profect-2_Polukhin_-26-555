import json


def load_metadata(filepath:str) -> dict:
    try:
        with open(filepath, encoding="utf-8") as file:
            metadata = json.load(file)
            return metadata
    except FileNotFoundError:
        return {}

def save_metadata(filepath:str, data:dict) -> None:
    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def wrong_value_message(value_repr:str) -> str:
    return f'Некорректное значение: <{value_repr}>. Попробуйте снова.'