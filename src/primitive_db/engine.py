import shlex

import prompt

from primitive_db import core, utils
from primitive_db.constants import METADATA_PATH


def welcome():
   
    print("Первая попытка запустить проект!"
          "\n\n"
          "***")
    
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
    while True:
        user_input = prompt.string("Введите команду: ")
        
        args = shlex.split(user_input, posix = False)
        if not args:
            continue
        
        try:
            command = args[0]
            if command == "help":
                print("\n")
                print_help()
            elif command == "create_table":
              
                # ожидаем имя функции, имя таблицы и хотя бы одну колонку
                if len(args) < 3: 
                    raise ValueError(" ".join(["Ошибка синтаксиса.",
                          "Ожидается имя таблицы и хотя бы одна колонка.", 
                          "Попробуйте снова."]))

                columns= []
                for arg in args[2:]:
                    
                    parts = arg.split(':')
                    if len(parts) != 2:
                        raise ValueError(utils.wrong_value_message(arg))
                    
                    column_name, column_type = parts
                    columns.append({"name": column_name, "type":column_type})

                core.create_table(metadata, args[1], columns)
                utils.save_metadata(METADATA_PATH, metadata)
            elif command == "list_tables":
                core.print_list_of_tables(metadata)
            elif command == "exit":
                break
            else:
                print(f"Функции <{command}> нет. Попробуйте снова.")
        except Exception as exc:
            print(exc)


def print_help():
    """Prints the help message for the current mode."""
   
    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> "
          "<столбец2:тип>.. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    
    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")
