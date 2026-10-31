import time


def handle_db_errors(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError:
            print(
                "Ошибка: Файл данных не найден. "
                "Возможно, база данных не инициализирована."
            )
        except KeyError as e:
            print(f"Ошибка: Таблица или столбец {e} не найден.")
            raise  # пробрасываем исключение для перехвата в engine.run
        except ValueError as e:
            print(f"Ошибка валидации: {e}")
            raise
        except Exception as e:
            print(f"Произошла непредвиденная ошибка: {e}")
            raise

    return wrapper


def confirm_action(action_name):

    def decorator(func):
        
        def wrapper(*args, **kwargs):
        
            answer = input(f"Вы уверены, что хотите выполнить \"{action_name}\"?[y/n]:")
            if answer.lower() not in ('y', "yes"):
                raise RuntimeError("Операция отменена пользователем!")
            return func(*args, **kwargs)
        
        return wrapper
    
    return decorator

def log_time(func):
    def wrapper(*args, **kwargs):
        start = time.monotonic()
        result = func(*args, **kwargs)
        finish = time.monotonic()

        duration = round(finish - start, 3)
        print(f'Функция \"{func.__name__}\" выполнилась за {duration} секунд')
        
        return result
    
    return wrapper
                  