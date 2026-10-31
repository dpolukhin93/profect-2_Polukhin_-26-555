import shlex

import prettytable
import prompt

from primitive_db import core, decorators, parser, utils
from primitive_db.constants import METADATA_PATH


def welcome():

    print("Первая попытка запустить проект!\n\n***")

    print_help()

    while True:
        command = prompt.string("Введите команду: ")
        if command == "help":
            print("\n")
            print_help()
        elif command == "exit":
            break


def run():

    print_help()
    metadata = utils.load_metadata(METADATA_PATH)
    if not metadata:
        print("Внимание! База данных не содержит ни одной таблицы."
              "Возможно, она не инициализирована.")
    elif metadata is None:
        print("Не удалось прочитать метаданные. Необходимо создать таблицы заново. "
              "Используйте команду create_table")
        
    while True:
        user_input = prompt.string("Введите команду: ")

        args = shlex.split(user_input, posix=False)
        if not args:
            continue

        try:
            command = args[0]
            args_len = len(args)
            if command == "help":
                print("\n")
                print_help()
            elif command == "create_table":
                command_create_table(metadata, args, args_len)
            elif command == "drop_table":
                command_drop_table(metadata, args, args_len)
            elif command == "insert":
                command_insert(metadata, args, args_len)
            elif command == "select":
                command_select(metadata, args, args_len)
            elif command == "update":
                command_update(metadata, args, args_len)
            elif command == "delete":
                command_delete(metadata, args, args_len)
            elif command == "info":
                command_info(metadata, args, args_len)
            elif command == "list_tables":
                core.print_list_of_tables(metadata)
            elif command == "exit":
                break
            else:
                print(f"Функции <{command}> нет. Попробуйте снова.")
        except SyntaxError as e:
            e_repr = str(e)
            print(f"Ошибка синтаксиса. {e_repr}")
        except Exception as exc:
            if exc.args:
                print(exc)


def command_info(metadata:dict, args:list, args_len:int):
    """Обработчик запроса info."""
    
    if args_len < 2:
        raise SyntaxError

    table_name = args[1]
    table_data = utils.load_table_data(table_name)
    core.print_info(table_name, metadata, table_data)


@decorators.confirm_action("удаление данных")
def command_delete(metadata:dict, args:list, args_len:int):
    """Обработчик запроса delete."""
    
    if args_len < 7 or args[1] != "from" or args[3] != "where":
        raise SyntaxError

    table_name = args[2]
    table_data = utils.load_table_data(table_name)
    where_clause = parser.parse_clause(metadata, table_name, args[4:])

    if not where_clause:
        raise ValueError("Не задано условие в секции where")

    core.delete(table_data, where_clause)
    utils.save_table_data(table_name, table_data)
    core.clear_table_cache(table_cache.cache, table_name)
    deleted_rows_repr = ", ".join(
                    f"{key}={value}" for key, value in where_clause.items()
                )
    print(
                    f"Запись с {deleted_rows_repr} успешно удалена из "
                    f"таблицы {table_name!r}"
                )


@decorators.log_time
def command_update(metadata:dict, args:list, args_len:int):
    """Обработчик запроса update."""
    
    if args_len < 10 or args[2] != "set" or "where" not in args:
        raise SyntaxError

    table_name = args[1]
    where_position = args.index("where")
    if args_len - where_position < 3:
        raise ValueError('Не задано условие в секции "where"')

    table_data = utils.load_table_data(table_name)
    tokens_for_parsing = args[3 : where_position]
    set_clause = parser.parse_clause(
                    metadata, table_name, tokens_for_parsing, "set"
                )

    tokens_for_parsing = args[where_position + 1 :]
    where_clause = parser.parse_clause(
                    metadata, table_name, tokens_for_parsing
                )

    updated_rows = core.update(table_data, set_clause, where_clause)
    for row in updated_rows:
        print(
                        f"Запись с ID = {row['ID']} в таблице {table_name!r} "
                        "успешно обновлена"
                    )

    utils.save_table_data(table_name, table_data)
    core.clear_table_cache(table_cache.cache, table_name)


@decorators.log_time
def command_select(metadata:dict, args:list, args_len:int):
    """Обработчик запроса select."""
  
    raise_syntax_error = False
    filtration = False
    if args_len < 3 or args[1] != "from":
        raise_syntax_error = True
    if args_len > 4:
        filtration = True
        if args[3] != "where":
            raise_syntax_error = True

    if raise_syntax_error:
        raise SyntaxError

    table_name = args[2]
    
    if filtration:
        where_clause = parser.parse_clause(metadata, table_name, args[4:])
    else:
        where_clause = {}

    def value_func():
        table_data = utils.load_table_data(table_name)
        result = core.select(table_data, where_clause)
        return result

    key = (table_name, tuple(sorted(where_clause.items())))
    result = table_cache(key, value_func)

    if result:
        pretty_print(result)
    else:
        print("Отсутствуют записи, удовлетворяющие условию запроса")


@decorators.log_time
def command_insert(metadata:dict, args:list[str], args_len:int):
    """Обработчик запроса insert."""
    
    if args_len < 7 or args[1] != "into" or args[3] != "values":
        raise SyntaxError

    table_name = args[2]
    table_data = utils.load_table_data(table_name)

    # распарсим секцию values
    values = parser.parse_insert_values(args[4:])

    table_data = core.insert(metadata, table_name, table_data, values)
    utils.save_table_data(table_name, table_data)
    core.clear_table_cache(table_cache.cache, table_name)

    print(
                    f"Запись с ID={table_data[-1]['ID']} "
                    f"успешно добавлена в таблицу {table_name}."
                )


def command_create_table(metadata:dict, args:list, args_len:int):
    """Обработчик запроса create_table."""
   
    # ожидаем имя функции, имя таблицы и хотя бы одну колонку
    if args_len < 3:
        raise SyntaxError(
                        " ".join(
                            [
                                "Ожидается имя таблицы и хотя бы одна колонка.",
                                "Попробуйте снова.",
                            ]
                        )
                    )

    columns = []
    table_name = args[1]
    for arg in args[2:]:
        parts = arg.split(":")
        if len(parts) != 2:
            raise ValueError(utils.wrong_value_message(arg))

        column_name, column_type = parts
        columns.append({"name": column_name, "type": column_type.lower()})

    core.create_table(metadata, table_name, columns)
    utils.save_metadata(METADATA_PATH, metadata)

    column_repr = ", ".join(
                    f"{col['name']}:{col['type']}" for col in metadata[table_name]
                )
    print(
                    f"Таблица {table_name!r} успешно "
                    f"создана со столбцами: {column_repr}"
                )


@decorators.confirm_action("удаление таблицы")
def command_drop_table(metadata:dict, args:list, args_len:int):

    if args_len < 2:
        raise SyntaxError
    
    table_name = args[1]
    core.drop_table(metadata, table_name)
    utils.delete_table_file(table_name)
    core.clear_table_cache(table_cache.cache, table_name)
    utils.save_metadata(METADATA_PATH, metadata)
    print(f"Таблица \"{table_name}\" успешно удалена.")


def print_help():
    """Prints the help message for the current mode."""

    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print(
        "<command> create_table <имя_таблицы> <столбец1:тип> "
        "<столбец2:тип>.. - создать таблицу"
    )
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")

    print("\n***Операции с данными***")
    print("Функции:")
    print(
        "<command> insert into <имя_таблицы> values (<значение1>, <значение2>, ...) "
        "- создать запись."
    )

    print(
        "<command> select from <имя_таблицы> where <столбец> = <значение> "
        "- прочитать записи по условию."
    )

    print("<command> select from <имя_таблицы> - прочитать все записи.")
    print(
        "<command> update <имя_таблицы> set <столбец1> = <новое_значение1> "
        "where <столбец_условия> = <значение_условия> "
        "- обновить запись."
    )

    print(
        "<command> delete from <имя_таблицы> where <столбец> = <значение>"
        " - удалить запись."
    )
    print("<command> info <имя_таблицы> - вывести информацию о таблице.")

    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")


def pretty_print(table_data: list[dict]):
    """Выводит результат запроса select в виде таблицы."""
    pretty_table = prettytable.PrettyTable()
    columns = list(table_data[0].keys())
    pretty_table.field_names = columns
    for row in table_data:
        pretty_table.add_row([row[column] for column in columns])

    print(pretty_table)


table_cache = core.create_cacher()