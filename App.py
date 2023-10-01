from modules.fileworker.FileWorker import JsonFileWorker
from modules.database.DatabaseLite import DataBase
from modules.globals.Functions import command


def main():
    jfw_app = JsonFileWorker()
    jfw_app.start()
    database_config = jfw_app.get_config_key(config_key="db_lite.config")

    db_app = DataBase(**database_config)
    db_app.start()
    while True:
        try:
            print(f"Active Category: [{db_app.temp_category}]")
            cmd = command(input("command: "))
            match cmd:
                case "create.category":
                    db_app.create_category(category=input("New Category: "), attributes=input("New Attributes: "))

                case "create.obj":
                    db_app.create_obj(attributes=input("Attributes: "), category=input("Category: "))

                case "data":
                    print(db_app.get_datas(category=input("Category: ")))

                case "backup":
                    db_app.backup()

                case "load.backup":
                    db_app.load_backup()

                case "stop" | "exit" | "esc":
                    db_app.shutdown()
                    break

                case _:
                    print(f"Unknown Command: {cmd}")
        except KeyboardInterrupt:
            print("Forced close!")
            db_app.shutdown()
            break


if __name__ == "__main__":
    main()
