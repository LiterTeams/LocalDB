from tabulate import tabulate
from modules.database.Converter import normalize_attribute, normalize_obj
from modules.globals.Functions import find_path, load_datas, write_datas, create_folder, create_json, trim, lower
from modules.globals.Errors import NotFoundError, DuplicateError
from os.path import abspath as alias


class DataBase:
    def __init__(self, **config):
        __slots__ = (
            "__general_directory", "__catalogs", "__names", "__formats",
            "__paths", "__experimental", "__virtual_tree", "__datas", "__temps", "temp_category",
            "db_status", "version",
        )

        self.__general_directory = alias(config["general_directory"])

        self.__catalogs = {
            "backup": f"{self.__general_directory}\\{config['backup_directory']}",
            "datas": f"{self.__general_directory}\\{config['data_directory']}",
            "types": f"{self.__general_directory}\\{config['type_directory']}",
        }

        self.__names = {
            "datas": config["data_name"],
            "types": config["type_name"],
        }

        self.__formats = {
            "backup": config["backup_format"],
            "datas": config["data_format"],
            "types": config["type_format"],
        }

        self.__paths = {
            "datas_backup": f"{self.__catalogs['backup']}\\{self.__names['datas']}-backup.{self.__formats['backup']}",
            "types_backup": f"{self.__catalogs['types']}\\{self.__names['types']}-backup.{self.__formats['types']}",
            "datas": f"{self.__catalogs['datas']}\\{self.__names['datas']}.{self.__formats['datas']}",
            "types": f"{self.__catalogs['types']}\\{self.__names['types']}.{self.__formats['types']}",
        }

        self.__experimental = config["experimental"]

        self.__virtual_tree = {}

        self.version: str = config["version"]

        self.__datas: dict = {}
        self.__temps: dict = {"keys": {}, "constants": {}, "templates": {}, "types": {}, "free_id": {}, "category": []}
        self.temp_category: str = ""

        self.db_status = False

    def __init_db(self):
        print("Init DataBase...")
        if find_path(self.__paths["datas"]) and find_path(self.__paths["types"]) and self.__experimental["data_category"] is False:
            self.__datas = load_datas(path=self.__paths["datas"])
            self.__temps = load_datas(path=self.__paths["types"])
        elif find_path(self.__paths["types"]) and self.__experimental["data_category"]:
            self.__temps = load_datas(path=self.__paths["types"])
            if self.__temps["category"]:
                for category in self.__temps["category"]:
                    data = load_datas(path=f"{self.__catalogs['datas']}\\{category}.{self.__formats['datas']}")
                    self.__datas[category] = data["datas"]
                    self.__virtual_tree[category] = False
        else:
            if find_path(self.__catalogs["datas"]) is False and self.__experimental["data_category"] is False:
                create_folder(folder_directory=self.__general_directory, folder_name="data")
                create_json(folder_directory=self.__catalogs["datas"], file_name=self.__names["datas"])
            if find_path(self.__catalogs["types"]) is False:
                create_folder(folder_directory=self.__general_directory, folder_name="types")
                create_json(folder_directory=self.__catalogs["types"], file_name=self.__names["types"])
            self.__create_db()
        self.db_status = True

    def __create_db(self):
        create_json(folder_directory=self.__catalogs["types"], file_name=self.__names["types"])
        write_datas(path=self.__paths["types"], datas=self.__temps)

    def start(self):
        self.__init_db()

    def shutdown(self):
        print("Saving Datas...")
        if self.__experimental["data_category"]:
            if self.__experimental["virtual_tree"]:
                for category in self.__temps["category"]:
                    write_datas(path=f"{self.__catalogs['datas']}\\{category}.{self.__formats['datas']}", datas={"datas":self.__datas[category]}) if self.__virtual_tree[category] else None
            else:
                for category in self.__temps["category"]:
                    write_datas(path=f"{self.__catalogs['datas']}\\{category}.{self.__formats['datas']}",datas={"datas": self.__datas[category]})
        else:
            write_datas(path=self.__paths["datas"], datas=self.__datas)
        write_datas(path=self.__paths["types"], datas=self.__temps)
        print("Datas Successful Was Saving")
        print("DataBase Successful Shutdown")

    def backup(self):
        print("Process Backup DB...")
        datas = load_datas(path=self.__paths["datas"])
        temps = load_datas(path=self.__paths["types"])
        write_datas(datas=datas, path=self.__paths["datas_backup"])
        write_datas(datas=temps, path=self.__paths["types_backup"])
        print("DB Successful Backup")

    def load_backup(self):
        print("Process Load Backup DB...")
        self.__datas = load_datas(path=self.__paths["datas_backup"])
        self.__temps = load_datas(path=self.__paths["types_backup"])
        print("DB Backup Successful Load")

    def __check_id(self,category: str):
        if category in self.__temps["free_id"] and len(self.__temps["free_id"][category]) != 0:
            free_id = self.__temps["free_id"][category].pop()
            return free_id
        else:
            all_id = set([item["id"] for item in self.__datas[category]]) if len(self.__datas[category]) > 0 else 0
            if all_id != 0:
                temporary_id = set([item for item in range(min(all_id), max(all_id) + 1)])
                result = temporary_id.difference(all_id)
                if len(result) > 0:
                    return result.pop()
                else:
                    return max(all_id) + 1
            else:
                return 1

    def __update_attributes(self, category: str, attributes: dict):
        self.__temps["keys"][category] = attributes["keys"]
        self.__temps["templates"][category] = attributes["templates"]
        self.__temps["constants"][category] = attributes["constants"]
        self.__temps["types"][category] = attributes["types"]
        self.__temps["category"].append(category)

    # =================== | Func-Create |================= #

    def create_category(self, category: str, attributes: str):
        category = trim(lower(category))
        if category in self.__temps["category"]:
            raise DuplicateError(value=category, function_name="DataBase - create category")

        attributes = normalize_attribute(category=category, attributes=attributes)
        self.__update_attributes(category=category, attributes=attributes)

        self.__datas[category] = list()
        self.temp_category = category
        if self.__experimental["data_category"]:
            create_json(folder_directory=self.__catalogs["datas"], file_name=category)
            write_datas(path=f"{self.__catalogs['datas']}\\{category}.{self.__formats['datas']}", datas={"datas":[]})
        if self.__experimental["virtual_tree"]:
            self.__virtual_tree[category] = False

    def create_obj(self,attributes,category=None):
        category = trim(lower(category))
        if category is not None or category != "":
            self.temp_category = category
        if self.temp_category not in self.__temps["category"]:
            raise NotFoundError(value=category, function_name="DataBase - create obj")

        templates = self.__temps["templates"][self.temp_category] if self.temp_category in self.__temps["templates"] else None

        keys = self.__temps["keys"][self.temp_category] if self.temp_category in self.__temps["keys"] else None

        types_obj2 = self.__temps["types"][self.temp_category].copy()
        types_obj = self.__temps["types"][self.temp_category].copy()

        obj = normalize_obj(attributes,types_obj,templates) if templates is not None else normalize_obj(attributes,types_obj)

        obj["id"] = self.__check_id(category=self.temp_category)

        if keys:
            for key in keys:
                if key not in templates and obj[key] == "null":
                    return

        self.__datas[category].append(obj)
        self.__temps["types"][category] = types_obj2

        if self.__experimental["virtual_tree"]:
            self.__virtual_tree[category] = True

    def get_datas(self,category=None):
        category = self.temp_category if category is None or category == "" else category
        if category in self.__temps["category"]:
            print(tabulate(self.__datas[category], headers="keys"))
        elif category is None or category == "":
            for category in self.__datas:
                print(tabulate(self.__datas[category],headers="keys"))
        else:
            print(f"Category: [{category}] Not Found!")

    def get_all(self):
        return self.__datas
