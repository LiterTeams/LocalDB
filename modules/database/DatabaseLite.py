from tabulate import tabulate
from modules.database.Converter import normalize_attribute, normalize_obj
from modules.globals.Functions import find_path, load_datas, write_datas, create_folder, create_json, delete_json, trim, lower, category_find
from modules.globals.Errors import NotFoundError, DuplicateError, NoContentError
from os.path import abspath as alias
from os import listdir


class DataBase:
    def __init__(self, **config):
        __slots__ = (
            "__general_directory", "__catalogs", "__names", "__formats",
            "__paths", "__experimental", "__virtual_tree", "__datas", "__temps", "temp_category",
            "db_status", "version", "__settings",
        )

        self.__general_directory = alias(config["file_directories"]["general"])

        self.__catalogs = {
            "backup": f"{self.__general_directory}\\{config['file_directories']['backup']}",
            "datas": f"{self.__general_directory}\\{config['file_directories']['datas']}",
            "types": f"{self.__general_directory}\\{config['file_directories']['types']}",
        }

        self.__names = config["file_names"]

        self.__formats = config["file_formats"]

        self.__settings = config["settings"]

        self.__experimental = config["experimental"]

        self.__paths = {
            "datas_backup": f"{self.__catalogs['backup']}\\{self.__names['datas']}-backup.{self.__formats['backup']}",
            "types_backup": f"{self.__catalogs['types']}\\{self.__names['types']}-backup.{self.__formats['types']}",
            "datas": f"{self.__catalogs['datas']}\\{self.__names['datas']}.{self.__formats['datas']}",
            "types": f"{self.__catalogs['types']}\\{self.__names['types']}.{self.__formats['types']}",
        }

        self.__virtual_tree = {}

        self.version: str = config["version"]

        self.__datas: dict = {}
        self.__temps: dict = {"keys": {}, "constants": {}, "templates": {}, "types": {}, "free_id": {}, "category": []}
        self.temp_category: str = ""

        self.db_status = False

    # =================== | Func-Protected |================= #

    def __init_db(self) -> None:
        if not find_path(self.__catalogs["datas"]):
            create_folder(folder_directory=self.__general_directory, folder_name="datas")

        if not self.__experimental["multiple_category"]:
            create_json(folder_directory=self.__catalogs["datas"], file_name=self.__names["data"])

        if not find_path(self.__catalogs["types"]):
            create_folder(folder_directory=self.__general_directory, folder_name="type")
            create_json(folder_directory=self.__catalogs["types"], file_name=self.__names["type"])

        if find_path(self.__paths["types"]) and self.__experimental["multiple_category"]:
            self.__temps = load_datas(path=self.__paths["types"])
            if self.__temps["category"] and not self.__experimental["dynamic_loading"]:
                for category in self.__temps["category"]:
                    data = load_datas(path=f"{self.__catalogs['datas']}\\{category}.{self.__formats['data']}")
                    self.__datas[category] = data["data"]
                    self.__virtual_tree[category] = False
            elif self.__temps["category"] and self.__experimental["dynamic_loading"]:
                for category in self.__temps["category"]:
                    self.__virtual_tree[category] = False
        else:
            create_json(folder_directory=self.__catalogs["types"], file_name=self.__names["types"])
            write_datas(path=self.__paths["types"], datas=self.__temps)
        self.db_status = True

    def __dynamic_loading(self, category:str) -> None:
        data = load_datas(path=f"{self.__catalogs['datas']}\\{category}.{self.__formats['datas']}")
        self.__datas[category] = data["datas"]

    def __update_attributes(self, category: str, attributes: dict) -> None:
        for key in ["keys","templates","constants","types"]:
            self.__temps[key][category] = attributes[key]
        self.__temps["category"].append(category)

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

    # =================== | Func-Public |================= #

    def start(self):
        self.__init_db()

    def shutdown(self) -> None:
        if self.__experimental["multiple_category"]:
            if self.__experimental["virtual_tree"]:
                for category in self.__temps["category"]:
                    if self.__virtual_tree[category]:
                        write_datas(path=f"{self.__catalogs['datas']}\\{category}.{self.__formats['datas']}", datas={"datas":self.__datas[category]})
            else:
                for category in self.__temps["category"]:
                    write_datas(path=f"{self.__catalogs['datas']}\\{category}.{self.__formats['datas']}",datas={"datas": self.__datas[category]})
        else:
            write_datas(path=self.__paths["datas"], datas=self.__datas)
        write_datas(path=self.__paths["types"], datas=self.__temps)

    def merge_category(self): ...

    def backup(self) -> None:
        if all([self.__experimental["multiple_category"], self.__settings["use_experimental"]]):
            for category in self.__temps["category"]:
                if category not in self.__datas:
                    data = load_datas(path=f"{self.__catalogs['datas']}\\{category}.{self.__formats['datas']}")
                    self.__datas[category] = data["datas"]
                for key, value in self.__datas.items():
                    write_datas(datas={"datas":value}, path=f"{self.__catalogs['backup']}\\datas\\{key}.{self.__formats['datas']}")
            write_datas(datas=self.__temps, path=f"{self.__catalogs['backup']}\\types\\{self.__names['types']}.{self.__formats['types']}")
        else:
            write_datas(datas=load_datas(path=self.__paths["datas"]), path=self.__paths["datas_backup"])
            write_datas(datas=load_datas(path=self.__paths["types"]), path=self.__paths["types_backup"])

    def load_backup(self) -> None:
        if all([self.__experimental["multiple_category"], self.__settings["use_experimental"]]):
            data_files = list(filter(lambda elem: elem.endswith(".json"),listdir(f"{self.__catalogs['backup']}\\datas")))
            type_files = list(filter(lambda elem: elem.endswith(".json"),listdir(f"{self.__catalogs['backup']}\\types")))
            if data_files:
                for file in data_files:
                    file_name = file.split(".")[0]
                    data = load_datas(path=f"{self.__catalogs['backup']}\\datas\\{file}")
                    self.__datas[file_name] = data["datas"]
                    self.__virtual_tree[file_name] = True
            if type_files:
                for file in type_files:
                    self.__temps = load_datas(path=f"{self.__catalogs['backup']}\\types\\{file}")
        else:
            self.__datas = load_datas(path=self.__paths["datas_backup"])
            self.__temps = load_datas(path=self.__paths["types_backup"])

    # =================== | Func-Create |================= #

    def create_category(self, category: str, attributes: str):
        self.temp_category = category_find(category, self.temp_category)
        if self.temp_category in self.__temps["category"]:
            raise DuplicateError(value=self.temp_category, function_name="DataBase - create category")

        attributes = normalize_attribute(category=self.temp_category, attributes=attributes)
        self.__update_attributes(category=self.temp_category, attributes=attributes)

        self.__datas[self.temp_category] = list()
        if all([self.__experimental["multiple_category"], self.__settings["use_experimental"]]):
            create_json(folder_directory=self.__catalogs["datas"], file_name=self.temp_category)
            write_datas(path=f"{self.__catalogs['datas']}\\{self.temp_category}.{self.__formats['datas']}", datas={"datas":[]})
        if all([self.__experimental["virtual_tree"], self.__settings["use_experimental"]]):
            self.__virtual_tree[self.temp_category] = False

    def create_obj(self, attributes, category=None):
        self.temp_category = category_find(category, self.temp_category)

        if self.temp_category not in self.__temps["category"]:
            raise NotFoundError(value=self.temp_category, function_name="DataBase - create obj")

        if self.temp_category not in self.__datas and self.__experimental["dynamic_loading"] and self.__experimental["multiple_category"]:
            self.__datas[self.temp_category] = load_datas(path=f"{self.__catalogs['datas']}\\{self.temp_category}.{self.__formats['datas']}")

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

    def create_key_attribute(self, attributes,category=None): ...

    def create_template_attribute(self, attributes, category=None): ...

    def create_const_attribute(self, attributes, category=None): ...

    # =================== | Func-Change |================= #

    def change_obj(self, obj_id:int, attributes:str, category): ...

    def change_template_attribute(self, attributes:str, category): ...

    # =================== | Func-Clear |================= #

    def __clear_attributes(self, obj, category):
        pass

    def clear_category(self, category) -> None:
        self.temp_category = category_find(category, self.temp_category)

        if self.temp_category not in self.__temps["category"]:
            raise NotFoundError(value=self.temp_category, function_name="DataBase - delete category")

        if self.__experimental["dynamic_loading"] and self.__settings["use_experimental"]:
            del self.__temps["free_id"][self.temp_category][:]
            if self.temp_category in self.__datas:
                del self.__datas[self.temp_category][:]
            else:
                self.__datas[self.temp_category] = list()
            self.__virtual_tree[self.temp_category] = True
        else:
            del self.__datas[self.temp_category][:]

    def clear_obj(self, obj_id:int, category):
        self.temp_category = category_find(category, self.temp_category)

        if self.temp_category not in self.__temps["category"]:
            raise NotFoundError(value=self.temp_category, function_name="DataBase - delete category")

    # =================== | Func-Delete |================= #

    def delete_category(self, category) -> None:
        self.temp_category = category_find(category, self.temp_category)

        if self.temp_category not in self.__temps["category"]:
            raise NotFoundError(value=self.temp_category, function_name="DataBase - delete category")

        if all([self.__experimental["dynamic_loading"], self.__settings["use_experimental"]]):
            if self.temp_category in self.__datas:
                del self.__datas[self.temp_category]
            for key in ["keys","constants","templates","types","free_id"]:
                if self.temp_category in self.__temps[key]:
                    del self.__temps[key][self.temp_category]
            self.__temps["category"].remove(self.temp_category)
            delete_json(folder_directory=f"{self.__catalogs['datas']}", file_name=f"{self.temp_category}.{self.__formats['datas']}")
            self.__virtual_tree[self.temp_category] = False
        else:
            del self.__datas[self.temp_category]

    def delete_obj(self, obj_id:int, category) -> None:
        self.temp_category = category_find(category,self.temp_category)

        if self.temp_category not in self.__temps["category"]:
            raise NotFoundError(value=category, function_name="DataBase - delete obj")

        experimental = [self.__experimental["dynamic_loading"], self.__experimental["multiple_category"], self.__settings["use_experimental"]]

        if self.temp_category not in self.__datas and all(experimental):
            self.__datas[self.temp_category] = load_datas(path=f"{self.__catalogs['datas']}\\{self.temp_category}.{self.__formats['datas']}")

        if len(self.__datas[category]) == 0:
            raise NoContentError(value=category, function_name="DataBase - delete obj")

        self.__datas[category] = list(filter(lambda elem: elem["id"] != obj_id, self.__datas[category]))
        self.__virtual_tree[category] = True

    def delete_key_attribute(self, attributes:str, category=None): ...

    def delete_template_attribute(self, attributes:str, category=None): ...

    def delete_const_attribute(self, attributes:str, category=None): ...

    # =================== | Func-Additional |================= #

    def get_datas(self,category=None):
        category = self.temp_category if category is None or category == "" else category
        if category in self.__temps["category"]:
            print(tabulate(self.__datas[category], headers="keys"))
        elif category is None or category == "":
            for category in self.__datas:
                print(tabulate(self.__datas[category],headers="keys"))
        else:
            print(f"Category: [{category}] Not Found!")
