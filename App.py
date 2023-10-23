import sqlite3
from modules.fileworker.FileWorker import JsonFileWorker
from modules.database.LiteDB import LiteDB
from modules.database.SQLiteDB import SQLiteDB
from modules.database.MongoDB import MongoDB
from modules.database.MySQLDB import MySQLDB
from modules.database.PostgreSQLDB import PostgreSQLDB
from modules.controllers.functions import command


def main():
    jfw_app = JsonFileWorker()
    jfw_app.start()
    db_lite_config = jfw_app.get_config_key(config_key="db_lite.config")
    db_sqlite_config = jfw_app.get_config_key(config_key="sqlite.config")

    lite_db = LiteDB()
    sql_db = SQLiteDB()

    sql_db.start(**db_sqlite_config)
    print(sql_db.select(table="test2", fetch="all"))
    sql_db.shutdown()
    #db_app.insert()

    # db_app = DataBase(**db_lite_config)
    # db_app.start()
    # db_app.shutdown()
    # while True:
    #     try:
    #         print(f"Active Category: [{db_app.temp_category}]")
    #         cmd = command(input("command: "))
    #         match cmd:
    #             case "create.category":
    #                 db_app.create_category(category=input("Category: "), attributes=input("Attributes: "))
    #             case "clear.category":
    #                 db_app.clear_category(category=input("Category: "))
    #             case "delete.category":
    #                 db_app.delete_category(category=input("Category: "))
    #
    #             case "create.key":
    #                 db_app.create_key_attribute(category=input("Category: "), attributes=input("Attributes: "))
    #             case "delete.key":
    #                 db_app.delete_key_attribute(category=input("Category: "), attributes=input("Keys: "))
    #
    #             case "create.template": ...
    #
    #             case "change.template":
    #                 db_app.change_template_attribute(category=input("Category: "), attributes=input("Attributes: "))
    #             case "del.template":
    #                 db_app.delete_template_attribute(category=input("Category: "), attributes=input("Templates: "))
    #
    #             case "delete.constant":
    #                 db_app.delete_const_attribute(category=input("Category: "), attributes=input("Constants: "))
    #
    #             case "create.obj":
    #                 db_app.create_obj(category=input("Category: "), attributes=input("Attributes: "))
    #             case "delete.obj":
    #                 db_app.delete_obj(category=input("Category: "), obj_id=int(input("Object ID:")))
    #
    #             case "data":
    #                 print(db_app.print_datas(category=input("Category: ")))
    #
    #             case "backup":
    #                 db_app.backup()
    #
    #             case "load.backup":
    #                 db_app.load_backup()
    #
    #             case "stop" | "exit" | "esc":
    #                 db_app.shutdown()
    #                 break
    #
    #             case _:
    #                 print(f"Unknown Command: {cmd}")
    #     except KeyboardInterrupt:
    #         print("Forced close!")
    #         db_app.shutdown()
    #         break


if __name__ == "__main__":
    main()
