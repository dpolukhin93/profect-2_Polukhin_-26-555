from primitive_db import decorators, parser, utils
from primitive_db.constants import AVAILABLE_TYPES, ID_COLUMN


@decorators.handle_db_errors
def create_table(metadata: dict, table_name: str, columns: list[dict]):

    if table_name in metadata:
        raise Exception(f"Таблица \"{table_name}\" уже существует")

    errors = []
    need_id = True
    id_index = 0
    for i, column in enumerate(columns):
        if column["name"] == ID_COLUMN["name"]:
            need_id = False
            id_index = i
            if column["type"] != ID_COLUMN["type"]:
                value_repr = f"{column['name']}:{column['type']}"
                errors.append(utils.wrong_value_message(value_repr))
                continue

        if column["type"] not in AVAILABLE_TYPES:
            value_repr = f"{column['name']}:{column['type']}"
            errors.append(utils.wrong_value_message(value_repr))

    if errors:
        raise ValueError("\n".join(error for error in errors))

    if need_id:
        columns.insert(0, ID_COLUMN.copy())
    else:
        columns.insert(0, columns.pop(id_index))

    metadata[table_name] = columns

    return metadata


@decorators.handle_db_errors
def drop_table(metadata: dict, table_name: str) -> dict:

    if table_name not in metadata:
        raise KeyError(table_name)

    metadata.pop(table_name)
    return metadata


def print_list_of_tables(metadata: dict) -> None:

    for key in metadata:
        print(f"- {key}")


@decorators.handle_db_errors
def insert(
    metadata: dict, table_name: str, table_data: list[dict], values: list
) -> list[dict]:

    if table_name not in metadata:
        raise KeyError(table_name)

    table_metadata = metadata[table_name]
    if len(values) != len(table_metadata) - 1:
        raise ValueError(
            "Ошибка. Указано неверное количество значений. "
            "Для вставки необходимо указать значения для всех полей. Попробуйте снова."
        )

    table_row = {}
    errors = []
    table_row[ID_COLUMN["name"]] = len(table_data) + 1
    for column_meta, column_value in zip(table_metadata[1:], values):
        try:
            typed_value = parser.convert_value(column_value, column_meta["type"])
        except ValueError as exc:
            if not exc.args:
                error_text = (
                    f"Не удалось привести значение {column_value!r} "
                   f"к типу {column_meta['type']!r}"
                )
            else:
                error_text = str(exc)

            errors.append(error_text)
            continue

        table_row[column_meta["name"]] = typed_value

    if errors:
        raise ValueError("\n".join(errors))


    table_data.append(table_row)

    return table_data


def select(table_data: list[dict], where_clause: dict) -> list[dict]:

    if not where_clause:
        return table_data

    result = [
        row
        for row in table_data
        if all(row.get(key) == value for key, value in where_clause.items())
    ]
    return result


def update(table_data: list[dict], set_clause: dict, where_clause: dict) -> list[dict]:

    rows_for_update = select(table_data, where_clause)
    for row in rows_for_update:
        row.update(set_clause)

    return rows_for_update


def delete(table_data: list[dict], where_clause: dict) -> list[dict]:

    ids_delete_rows = set(id(row) for row in select(table_data, where_clause))
    i = len(table_data)
    while i > 0:
        if not ids_delete_rows:
            break

        i -= 1
        row_id = id(table_data[i])
        if row_id in ids_delete_rows:
            table_data.pop(i)
            ids_delete_rows.discard(row_id)

    return table_data


@decorators.handle_db_errors
def print_info(table_name: str, metadata: dict, table_data: list[dict]) -> None:

    if table_name not in metadata:
        raise KeyError(table_name)

    print(f"Таблица: {table_name}")
    columns_pepr = ", ".join(
        f"{column['name']}:{column['type']}" for column in metadata[table_name]
    )
    print(f"Стоблцы: {columns_pepr}")
    print(f"Количество записей {len(table_data)}")


def create_cacher():
    cache = {}

    def cache_result(key, value_func):
        if key in cache:
            return cache[key]
        result = value_func()
        cache[key] = result
        return result

    cache_result.cache = cache
    return cache_result  


def clear_table_cache(cache:dict, table_name:str):
    
    for key in list(cache):
        if key[0] == table_name:
            del cache[key]