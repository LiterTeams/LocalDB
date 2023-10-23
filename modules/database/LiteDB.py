from tabulate import tabulate
from modules.database.Converter import normalize_attribute, normalize_obj
from modules.controllers.functions import find_path, load_datas, write_datas, create_folder, delete_json, alias, category_find, create_file
from modules.errors.Errors import NotFoundError, DuplicateError, NoContentError, InitializationError
from functools import reduce
from os import listdir


class LiteDB:
    def __init__(self, **config):
        __slots__ = (
            "__catalogs", "__paths", "__virtual_tree", "__datas",
            "__temps", "temp_category", "__status", "__version", "__settings",
        )

        self.__catalogs = {
            "general": alias(config.get("file_directories").get("general")),
            "backup": config.get("file_directories").get("backup"),
            "datas": config.get("file_directories").get("datas"),
            "types": config.get("file_directories").get("types"),
        }

        self.__settings = config.get("settings")

        self.__version: str = config.get("version")

        self.__datas: dict = {}
        self.__virtual_tree = {}
        self.__temps: dict = {"keys": {}, "constants": {}, "templates": {}, "types": {}, "free_id": {}, "category": []}
        self.temp_category: str = ""

        self.__status = False

    # =================== | Protected |================= #

    def __init_db(self) -> None:
        r"""Инициализация БД. Срабатывает при старте."""
        try:
            self.__catalogs.update({
                "backup": f"{self.__catalogs["general"]}\\{self.__catalogs["backup"]}",
                "datas": f"{self.__catalogs.get("general")}\\{self.__catalogs["datas"]}",
                "types": f"{self.__catalogs.get("general")}\\{self.__catalogs["types"]}",
            })
        except Exception:
            raise InitializationError(value="",function_name="Database Lite - config init")

        if not find_path(path=f"{self.__catalogs.get("general")}\\public"):
            create_folder(folder_directory=self.__catalogs.get("general"), folder_name="public")

        if not find_path(path=self.__catalogs.get("backup")):
            create_folder(folder_directory=f"{self.__catalogs.get("general")}\\private", folder_name="backup")

        if not find_path(path=self.__catalogs.get("datas")):
            create_folder(folder_directory=f"{self.__catalogs.get("general")}\\public", folder_name="datas")

        if not find_path(path=self.__catalogs.get("types")):
            create_folder(folder_directory=f"{self.__catalogs.get("general")}\\public", folder_name="types")

        if not find_path(path=f"{self.__catalogs.get("types")}\\types.json"):
            create_file(folder_directory=self.__catalogs.get("types"), file_name="types", file_format="json")

        if find_path(path=f"{self.__catalogs.get("types")}\\types.json"):
            temps = load_datas(path=f"{self.__catalogs.get("types")}\\types.json")
            self.__temps = temps if temps else self.__temps
            if self.__temps.get("category"):
                for category in self.__temps.get("category"):
                    self.__global_handler(category=category, check_data=True)
                    self.__virtual_tree[category] = False
        self.__status = True

    def __update_attributes(self, category: str, attributes: dict) -> None:
        r"""Обновление атрибутов. Срабатывает при создании категории."""
        for key in ["keys","templates","constants","types"]:
            self.__temps[key][category] = attributes[key]
        self.__temps["category"].append(category)

    def __check_id(self,category: str) -> int:
        r"""Поиск свободных ID в категории"""
        if self.__temps.get("free_id").get(category):
            return self.__temps.get("free_id").get(category).pop()
        if self.__datas.get(category):
            datas_id = set(data.get("id") for data in self.__datas.get(category))
            self.__temps["free_id"][category] = list(set([item for item in range(min(datas_id) - min(datas_id) + 1, max(datas_id) + 1)]).difference(datas_id))
            return self.__temps["free_id"][category].pop() if len(self.__temps["free_id"][category]) > 0 else max(datas_id) + 1
        return 1

    def __dynamic_load(self, category:str, path:str, file_name:str | None = None, file_format:str | None = None) -> None:
        r"""Динамически загружает данные, которые не обходимы в данный момент."""
        try:
            data = load_datas(path, file_name, file_format)
            self.__datas[category] = data.get("datas")
        except FileNotFoundError:
            raise NotFoundError(value="", function_name="")

    def __global_handler(self, category: str, check_category_data=True, check_category_duplicate=False, check_data_content=False, check_data=False, check_type=False, function_name: str = "") -> None:
        self.temp_category = category_find(category, self.temp_category)

        if all([check_category_data, self.temp_category not in self.__temps.get("category")]):
            raise NotFoundError(value=self.temp_category, function_name="")

        if all([check_category_duplicate, self.temp_category in self.__temps.get("category")]):
            raise DuplicateError(value=self.temp_category, function_name=function_name)

        if check_type:
            self.__temps = load_datas(path=self.__catalogs.get("types"), file_name="types", file_format="json")

        if all([check_data, self.temp_category not in self.__datas]):
            self.__dynamic_load(category=self.temp_category, path=f"{self.__catalogs.get("datas")}", file_name=self.temp_category, file_format="json")

        if all([check_data_content, len(self.__datas.get(self.temp_category)) == 0 if self.temp_category in self.__datas else False]):
            raise NoContentError(value=self.temp_category, function_name="DataBase - ???")

    # =================== | Public |================= #

    def start(self) -> None:
        r"""Запуск БД"""
        self.__init_db()

    def shutdown(self) -> None:
        r"""Закрытие БД и сохранение изменений"""
        for category in self.__temps.get("category"):
            if self.__virtual_tree.get(category):
                write_datas(datas={"datas":self.__datas.get(category)}, path=f"{self.__catalogs.get("datas")}", file_name=category, file_format="json")
        write_datas(datas=self.__temps, path=f"{self.__catalogs.get("types")}", file_name="types", file_format="json")

    def backup(self) -> None:
        r"""Резервная копия БД"""
        for category in self.__temps.get("category"):
            if category not in self.__datas:
                self.__dynamic_load(category=category, path=self.__catalogs.get("datas"), file_name=category, file_format="json")
            for value in self.__datas.values():
                write_datas(datas={"datas": value}, path=f"{self.__catalogs.get("backup")}\\datas", file_name=category, file_format="json")
        write_datas(datas=self.__temps, path=f"{self.__catalogs.get("backup")}\\types", file_name="types", file_format="json")

    def load_backup(self) -> None:
        r"""Загрузка резервной копии БД"""
        data_files = list(filter(lambda elem: elem.endswith(".json"),listdir(f"{self.__catalogs.get("backup")}\\datas")))
        type_files = list(filter(lambda elem: elem.endswith(".json"),listdir(f"{self.__catalogs.get("backup")}\\types")))
        if data_files:
            for file in data_files:
                file_name = file.split(".")[0]
                data = load_datas(path=f"{self.__catalogs.get("backup")}\\datas\\{file}")
                self.__datas[file_name] = data.get("datas")
                self.__virtual_tree[file_name] = True
        if type_files:
            for file in type_files:
                self.__temps = load_datas(path=f"{self.__catalogs.get("backup")}\\types\\{file}")

    # =================== | Func-Create |================= #

    def create_category(self, category: str, attributes: str):
        r"""Создание новой категории."""
        self.__global_handler(category=category, check_category_data=False, check_category_duplicate=True)

        attributes = normalize_attribute(category=self.temp_category, attributes=attributes)
        self.__update_attributes(category=self.temp_category, attributes=attributes)

        self.__datas[self.temp_category] = list()
        write_datas(datas={"datas":[]}, path=self.__catalogs.get("datas"), file_name=self.temp_category, file_format="json")
        self.__virtual_tree[self.temp_category] = False

    def create_obj(self, attributes, category=None):
        self.__global_handler(category=category, function_name="DataBase - create obj", check_data=True)

        templates = self.__temps["templates"].get(self.temp_category) if self.temp_category in self.__temps["templates"] else None

        keys = self.__temps["keys"].get(self.temp_category) if self.temp_category in self.__temps["keys"] else None

        types_obj = self.__temps["types"][self.temp_category].copy()

        obj = normalize_obj(attributes,types_obj,templates) if templates is not None else normalize_obj(attributes,types_obj)

        obj["id"] = self.__check_id(self.temp_category)

        if keys:
            for key in keys:
                if obj[key] == "null":
                    raise NoContentError(value=key, function_name="DataBase - create obj")

        self.__datas[self.temp_category].append(obj)
        self.__temps["types"][self.temp_category] = types_obj

        self.__virtual_tree[self.temp_category] = True

    def create_attribute(self, attribute_type:str, attributes:str, category:str | None = None):
        self.__global_handler(category=category, function_name="DataBase - delete category", check_data=True)

    def create_key_attribute(self, attributes,category=None):
        self.__global_handler(category=category, function_name="DataBase - delete category", check_data=True)

        keys = reduce(lambda acc, value: dict(acc, **value), [{elem.split(":")[0]:elem.split(":")[1]} for elem in attributes.split(" ")])
        datas = self.__datas[self.temp_category]

        if set(keys.keys()).intersection(set(self.__temps["keys"][self.temp_category])):
            raise DuplicateError(value="", function_name="")

        if datas:
            if set(keys.keys()).intersection(set(datas[0].keys())):
                raise DuplicateError(value="", function_name="")
            for data in datas:
                for key in list(keys.keys()):
                    data[key] = "undefined"
        for key in list(keys.keys()):
            self.__temps["keys"][self.temp_category].append(key)
            self.__temps["types"][self.temp_category][key] = keys[key]

        self.__virtual_tree[self.temp_category] = True

    def create_template_attribute(self, attributes, category=None):
        self.__global_handler(category=category, function_name="DataBase - delete category", check_data=True)

        templates = reduce(lambda acc, value: dict(acc, **value), [{elem.split(":")[0]:elem.split(":")[1]} for elem in attributes.split(" ")])
        datas = self.__datas[self.temp_category]

        if set(templates.keys()).intersection(set(self.__temps["templates"][self.temp_category])):
            raise DuplicateError(value="", function_name="")

        if datas:
            if set(templates.keys()).intersection(set(datas[0].keys())):
                raise DuplicateError(value="", function_name="")
            for data in datas:
                for key in list(templates.keys()):
                    data[key] = templates[key].split("=")[1]
        for key in list(templates.keys()):
            self.__temps["templates"][self.temp_category][key] = templates[key].split("=")[1]
            self.__temps["types"][self.temp_category][key] = templates[key].split("=")[0]

        self.__virtual_tree[self.temp_category] = True

    def create_const_attribute(self, attributes, category=None):
        self.__global_handler(category=category, function_name="DataBase - delete category", check_data=True)

        constants = reduce(lambda acc, value: dict(acc, **value), [{elem.split(":")[0]:elem.split(":")[1]} for elem in attributes.split(" ")])
        datas = self.__datas[self.temp_category]

        if set(constants.keys()).intersection(set(self.__temps["constants"][self.temp_category])):
            raise DuplicateError(value="", function_name="")

        if datas:
            if set(constants.keys()).intersection(set(datas[0].keys())):
                raise DuplicateError(value="", function_name="")
            for data in datas:
                for key in list(constants.keys()):
                    data[key] = "undefined"
        for key in list(constants.keys()):
            self.__temps["constants"][self.temp_category].append(key)
            self.__temps["types"][self.temp_category][key] = constants[key]

        self.__virtual_tree[self.temp_category] = True


    # =================== | Func-Change |================= #

    def change_obj(self, obj_id:int, attributes:str, category): ...

    def change_template_attribute(self, attributes:str, category):
        self.__global_handler(category=category, function_name="DataBase - change template attribute")

        attributes = reduce(lambda acc,value: dict(acc, **value),[{attr.split("=")[0]:attr.split("=")[1]} for attr in attributes.split(" ")])

        templates = self.__temps["templates"][self.temp_category] if self.temp_category in self.__temps["templates"] else None

        for key in list(attributes.keys()):
            if key not in list(templates.keys()) or not templates:
                raise NotFoundError(value="", function_name="DataBase - change template attribute")
            templates[key] = attributes[key]

    # =================== | Func-Clear |================= #

    def clear_category(self, category) -> None:
        r"""Очистка категории от данных"""
        self.__global_handler(category=category)

        if self.temp_category in self.__datas:
            del self.__datas[self.temp_category][:]
            del self.__temps["free_id"][self.temp_category][:]
        else:
            self.__datas[self.temp_category] = list()
            self.__temps["free_id"][self.temp_category] = list()

        self.__virtual_tree[self.temp_category] = True

    def clear_obj(self, obj_id:int, category:str):
        self.__global_handler(category=category, function_name="DataBase - clear obj", check_data=True)
        datas = self.__datas[self.temp_category]
        datas_types = self.__temps["types"][self.temp_category]
        datas_templates = self.__temps["templates"][self.temp_category]
        datas_constants = self.__temps["constants"][self.temp_category]

        if not datas:
            raise NoContentError(value="", function_name="Data Base - clear_obj")

        if obj_id not in {data["id"] for data in datas}:
            raise NotFoundError(value=obj_id, function_name="Data Base - clear_obj")

        for data in datas:
            if data["id"] == obj_id:
                for key in data:
                    pass




        self.__virtual_tree[self.temp_category] = True

    # =================== | Func-Delete |================= #

    def delete_category(self, category:str | None = None) -> None:
        self.__global_handler(category=category, check_data=True)

        if self.temp_category in self.__datas:
            del self.__datas[self.temp_category]

        for key in filter(lambda x: x != "category", self.__temps.keys()):
            if self.temp_category in self.__temps[key]:
                del self.__temps[key][self.temp_category]
        self.__temps["category"].remove(self.temp_category)
        delete_json(folder_directory=f"{self.__catalogs.get("datas")}", file_name=f"{self.temp_category}.json")
        self.__virtual_tree[self.temp_category] = False

    def delete_obj(self, obj_id:int, category:str | None = None) -> None:
        r"""Удаление объекта из категории"""
        self.__global_handler(category=category, check_data=True, check_data_content=True)
        datas = self.__datas.get(self.temp_category)
        self.__datas[self.temp_category] = list(filter(lambda data: data.get("id") != obj_id, datas))
        self.__virtual_tree[category] = True

    def delete_attribute(self, type_attribute:str, attributes:str, category:str | None = None) -> None:
        self.__global_handler(category=category)

        attrs = set(attributes.split(","))
        data_attributes = set(self.__temps.get(type_attribute).get(self.temp_category))

        if not attrs.intersection(data_attributes):
            raise NotFoundError(value=attrs, function_name=f"DataBase - delete {type_attribute} attribute")
        for attr in attrs:
            data_attributes.remove(attr)

    def delete_key_attribute(self, attributes:str, category:str | None = None) -> None:
        r"""Удаляет ключевой атрибут. Не изменяет данные."""
        self.__global_handler(category=category)

        attrs = set(attributes.split(","))
        data_keys = set(self.__temps.get("keys").get(self.temp_category))

        if not attrs.intersection(data_keys):
            raise NotFoundError(value=attrs, function_name="DataBase - delete key attribute")
        for attr in attrs:
            data_keys.remove(attr)

    def delete_template_attribute(self, attributes:str, category=None):
        r"""Удаляет шаблон атрибута. Не изменяет данные."""
        self.__global_handler(category=category, function_name="DataBase - delete template")

        attrs = set(attributes.split(","))
        data_templates = set(self.__temps.get("templates").get(self.temp_category))

        if not attrs.intersection(data_templates):
            raise NotFoundError(value=attrs, function_name="DataBase - delete template attribute")
        for attr in attrs:
            data_templates.remove(attr)

    def delete_const_attribute(self, attributes:str, category=None):
        self.__global_handler(category=category, function_name="DataBase - delete keys")

        attributes = attributes.split(",")

        consts = self.__temps["constants"][self.temp_category] if self.temp_category in self.__temps["constants"] else None

        for key in attributes:
            if key not in consts or not consts:
                raise NotFoundError(value="", function_name="DataBase - delete template attribute")
            consts.remove(key)

    # =================== | Func-Additional |================= #

    def print_datas(self,category=None, page:int = 1) -> None:
        r"""Выводит информацию о данных категории"""
        self.__global_handler(category=category, check_data=True)
        if self.temp_category not in self.__temps.get("category"):
            raise NotFoundError(value=self.temp_category, function_name="DataBase - get datas")
        print(tabulate(self.__datas.get(self.temp_category)[:256 * page], headers="keys"))
        if input("Next Page? [Y/n]: ") in ["Y","y"]:
            self.print_datas(category=category, page=page + 1)

    @property
    def version(self): return self.__version

    @property
    def status(self): return self.__status


