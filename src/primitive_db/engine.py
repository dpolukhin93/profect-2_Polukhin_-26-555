import prompt


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
        else:
            break
    

def print_help():
    print("<command> exit - выйти из программы")
    print("<command> help - справочная информация")
