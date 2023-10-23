from sqlite3 import connect
from ..controllers.functions import alias, find_path, create_folder, trim
from ..errors.Errors import InitializationError, NotFoundError, Conflict


def _convert_to_object(response: list | tuple, headers: list) -> list | dict:
    datas = []
    keys = [trim(header).split(" ")[0] for header in headers]
    keys.insert(0, "id")
    for data in response:
        datas.append(dict(zip(keys, data)))
    return datas if len(datas) > 1 else datas[0]


class SQLiteDB:
    def __init__(self):
        self.__db = None
        self.__sql = None
        self.__settings: dict | None = None
        self.__directories: dict | None
        self.__status: bool = False

    def __config_init(self, config) -> None:
        try:
            self.__settings = config["settings"]
            self.__directories = config["file_directories"]
            self.__directories.update({"general": f"{alias(self.__directories.get("general"))}",})
            self.__directories.update({"datas": f"{self.__directories.get("general")}\\{self.__directories.get("datas")}"})
        except Exception:
            raise InitializationError(value="sqlite.config",function_name="Database SQLite - config init")

        if not find_path(path=f"{self.__directories.get("general")}\\public"):
            create_folder(folder_directory=self.__directories.get("general"), folder_name="public")

        if not find_path(path=f"{self.__directories.get("general")}\\public\\database"):
            create_folder(folder_directory=f"{self.__directories.get("general")}\\public", folder_name="database")

        if not find_path(path=self.__directories.get("datas")):
            create_folder(folder_directory=f"{self.__directories.get("general")}\\public\\database", folder_name="sqlite")

        self.__db = connect(f"{self.__directories.get("datas")}\\{config.get("database_name")}")
        self.__sql = self.__db.cursor()
        self.__status = True

    def start(self, **config) -> None: self.__config_init(config)

    def shutdown(self) -> None: self.__db.close()

    def create_table(self):
        self.__sql.execute("""CREATE TABLE IF NOT EXISTS test2 (developer text, test test)""")
        self.__db.commit()

    def select(self, table:str, select:str = "*", fetch="all", many=1, convert_to_object=True) -> list | tuple | dict:
        match fetch:
            case "all": response = self.__sql.execute(f"SELECT rowid, {select} FROM {table}").fetchall()
            case "one": response = list(self.__sql.execute(f"SELECT rowid, {select} FROM {table}").fetchone())
            case "many": response = self.__sql.execute(f"SELECT rowid, {select} FROM {table}").fetchmany(many)
            case _: raise NotFoundError(value=fetch, function_name="Database SQLite - select")

        if convert_to_object:
            pre_headers = self.__sql.execute(f"SELECT sql FROM sqlite_master WHERE tbl_name='{table}' AND type='table'").fetchone()
            headers = str(str(str(pre_headers[0]).split("(")[1]).split(")")[0]).split(",")
            return _convert_to_object(response,headers)

        return response

    def insert(self):
        self.__sql.execute("INSERT INTO test2 VALUES ('Thunder Light', 'hello')")
        self.__db.commit()
