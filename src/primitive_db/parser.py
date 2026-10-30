from primitive_db.constants import AVAILABLE_TYPES


def parse_clause(
    metadata: dict,
    table_name: str,
    clause_tokens: list[str],
    clause_type: str = "where",
) -> dict:

    table_metadata = metadata[table_name]
    awaited_format = "Ожидается запись вида <столбец> = <значение>"
    parsing_error = f"Ошибка в секции {clause_type!r}. " + awaited_format

    if len(clause_tokens) % 3 != 0:
        # Каждое выражение в set и where должно состоять из трех частей
        raise ValueError(parsing_error)

    result = {}
    errors = []
    for i in range(0, len(clause_tokens), 3):
        column, operator, value = clause_tokens[i : i + 3]
        if operator != "=":
            errors.append(
                f"Неверный форма условия {clause_tokens[i : i + 3]!r}. "
                + awaited_format
            )
            continue

        column_meta = next(
            (
                column_data
                for column_data in table_metadata
                if column_data["name"] == column
            ),
            None,
        )

        if column_meta is None:
            error = (
                f"Колонка {column!r} отсутствует в метаданных таблицы {table_name!r}"
            )
            errors.append(error)
            continue

        try:
            typed_value = convert_value(value, column_meta["type"])
        except ValueError as exc:
            errors.append(
                f"Недопустимое значение {value!r} для колонки {column!r}: {exc}"
            )
            continue

        result[column] = typed_value

    if errors:
        raise ValueError("\n".join(errors))

    return result


def convert_value(value: str, target_type: str) -> int | str | bool:

    if target_type == AVAILABLE_TYPES[0]:  # bool
        lower_value = value.strip().lower()
        if lower_value == "true":
            return True
        elif lower_value == "false":
            return False
    elif target_type == AVAILABLE_TYPES[1]:  # int
        strip_value = value.strip()
        body = strip_value[1:] if strip_value[:1] == "-" else strip_value
        if body.isascii() and body.isdigit():
            return int(strip_value)
    elif target_type == AVAILABLE_TYPES[2]:  # str
        # 1. Строка обязательно должна быть заключена в одинаковые кавычки
        # 2. Строка внутри кавычек не должна быть пустой
        if value[0] == value[-1] and value[0] in "'\"" and value[1:-1].strip():
            return value[1:-1]
    else:  # недопустимый тип
        raise ValueError(f"Ошибка. Недопустимый тип {target_type}")

    # некорректное значение (не прошло проверки выше)
    raise ValueError
