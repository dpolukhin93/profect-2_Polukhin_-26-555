from primitive_db import decorators
from primitive_db.constants import AVAILABLE_TYPES


@decorators.handle_db_errors
def parse_clause(
    metadata: dict,
    table_name: str,
    clause_tokens: list[str],
    clause_type: str = "where",
) -> dict:
    """Разбирает пользовательский ввод для выражений set и where."""

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
    """Приводит переданное значение к целевому типу из метаданных"""

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

def parse_insert_values(values:list[str]):
    """Проверяет массив токенов на соответствие (Значение1, Значение2, Значение3).
    Убирает обрамляющие скобки и запятые между значениями.
    Токены между кавычками склеивает в общий токен-строку"""
    
    raise_syntax_error = False
    if not values[0].startswith("("):
        raise_syntax_error = True
    if not values[-1].endswith(")"):
        raise_syntax_error = True

    values[0] = values[0].removeprefix("(")
    values[-1] = values[-1].removesuffix(")")

    if values[-1].endswith(","):
        raise_syntax_error = True

    insert_args = convert_arguments(values)
    
    for i, insert_arg in enumerate(insert_args[: len(insert_args) - 1]):
        if not insert_arg.endswith(","):
            raise_syntax_error = True
            continue
        insert_args[i] = insert_arg.removesuffix(",")

    if raise_syntax_error:
        raise SyntaxError

    return insert_args

def convert_arguments(values):
    
    insert_args =[]
    in_quotes = False
    open_quote = ""
    for value in values:
        if in_quotes:
            insert_args[-1] += f" {value}"
            if value.endswith(open_quote) or value.endswith(open_quote + ","):
                in_quotes = False
        else:
            insert_args.append(value)
            
            # исключаем случаи когда токен целиком в кавычках
            if value.startswith(('"', "'")) and not(
                len(value) >= 2 and value[0] == value.rstrip(',')[-1]
                ):
                in_quotes = True
                open_quote = value[0]

    if in_quotes:
            raise SyntaxError
                
    return insert_args
