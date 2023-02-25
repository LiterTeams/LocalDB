import json
import os
from texttable import Texttable
from corrector import lowers
from tabulate import *
from converter import *
from error import *


def load_datas(path:str):
    with open(path, "r") as file:
        return json.load(file)


def write_datas(path:str, datas:dict):
    with open(path, "w") as file:
        json.dump(datas, file, indent=2, ensure_ascii=False)


def create_json(path:str,name:str):
    path = f"{path}/{name}.json"
    write_datas(path=path, datas={})


def create_folder(name:str):
    os.makedirs(name)


def create_id_list(obj_id) -> list:
    keys = list()
    pre_keys = [key for key in obj_id.split(",")] if "," in obj_id else [key for key in obj_id.split("-")]

    for key in pre_keys:
        if "-" in key:
            temp_keys = [int(item) for item in key.split("-")]
            counter = temp_keys[1] - temp_keys[0] + 1
            [keys.append(temp_keys[0] + item) for item in range(counter)]
        elif len(pre_keys) == 2 and pre_keys[1] > pre_keys[0]:
            temp_keys = [int(item) for item in pre_keys]
            counter = temp_keys[1] - temp_keys[0] + 1
            [keys.append(temp_keys[0] + item) for item in range(counter)]
        else:
            keys.append(int(key))
    return keys


class DataBase:

    # ================== | Func-General |================#

    def __init__(self):
        self.db_status: False
        self.directory = "../jsons"
        self.format = "json"

        self.db_name = "Project"
        self.temp_name = "Temp"

        self.version = "Beta 3.0"

        self.db_path = f"{self.directory}/{self.db_name}.{self.format}"
        self.temp_path = f"{self.directory}/{self.temp_name}.{self.format}"

        self.__datas = dict()
        self.__temps = dict()
        self.__free_id = dict()
        self.temp_category = str()

        self.db_status = False

    def start(self):
        status = self.__check_db(path=self.db_path)
        if status:
            self.db_status: True
            print("DataBase Successful Load")
        else:
            print("DataBase Error Load")
            raise KeyError()

    def shutdown(self):
        print("Saving Datas...")
        self.__temps["ids"] = {key:list(self.__free_id[key]) for key in self.__free_id}
        write_datas(path=self.db_path,datas=self.__datas)
        write_datas(path=self.temp_path, datas=self.__temps)
        print("Datas Successful Was Saving")
        print("DataBase Successful Shutdown")

    def backup(self):
        print("Process Backup DataBase...")
        datas = load_datas(path=self.db_path)
        temps = load_datas(path=self.temp_path)
        write_datas(datas=datas, path=f"{self.directory}/{self.db_name}-Backup.{self.format}")
        write_datas(datas=temps, path=f"{self.directory}/{self.temp_name}-Backup.{self.format}")
        print("DataBase Successful Backup")

    def load_backup(self):
        print("Process Load Backup DataBase...")
        self.__datas = load_datas(path=f"{self.directory}/{self.db_name}-Backup.{self.format}")
        self.__temps = load_datas(path=f"{self.directory}/{self.temp_name}-Backup.{self.format}")
        print("DataBase Backup Successful Load")

    def __check_db(self, path: str):
        if os.path.exists(path):
            print("Loading DataBase...")
            self.__datas = load_datas(path=self.db_path)
            self.__temps = load_datas(path=self.temp_path)
            self.temp_category = self.__temps["temp_category"]
            self.__free_id = {key:set(self.__temps["ids"][key]) for key in self.__temps["ids"]}
            self.bd_status = True
            status = True
        else:
            if lowers(input("Create DataBase? [Y/n]:")) == "y":
                if os.path.exists("../jsons") is False:
                    create_folder("../jsons")
                status = self.__create_db()
            else:
                status = False
        return status

    def __check_id(self,category: str):
        if category in self.__free_id and len(self.__free_id[category]) != 0:
            print(self.__free_id)
            free_id = self.__free_id[category].pop()
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

    def __create_db(self):
        self.__temps["keys"] = dict()
        self.__temps["complete"] = dict()
        self.__temps["constants"] = dict()
        self.__temps["types"] = dict()
        self.__temps["category"] = list()
        self.create_category(category="Developers",attributes="role:=list @sites[no-site]:=list !programming-language:=list")
        self.create_obj(category="Developers",attributes="role:=coder,artist,dnd programming-language:=Python,JavaScript,C++ sites:=https://vk.com/clyoucker,https://vk.com/litesolidcore")
        return True

    # =================== | Func-Create |================= #

    def create_category(self,category: str, attributes: str):
        attributes = normalize_attribute(category=category,attributes=attributes)

        self.__temps["keys"][category] = attributes["keys"][category] if attributes["keys"] else tuple()
        self.__temps["complete"][category] = attributes["complete"][category] if attributes["complete"] else dict()
        self.__temps["constants"][category] = attributes["constants"][category] if attributes["constants"] else tuple()

        self.__temps["types"][category] = attributes["types"]
        self.__temps["category"].append(category)

        self.__datas[category] = list()
        self.temp_category = category
        print(f"Category: [{category}] Successful Created")

    def create_obj(self,attributes,category=None):
        category = self.temp_category if category is None or category == "" else category
        if category in self.__temps["category"]:
            complete = self.__temps["complete"][category] if category in self.__temps["complete"] else None
            pre_obj = dict([attribute.split(":=") for attribute in attributes.split(" ")])
            types_obj = convert_format(self.__temps["types"][category].copy())
            obj = normalize_obj(pre_obj,types_obj,complete) if complete is not None else normalize_obj(pre_obj,types_obj)
            obj["id"] = self.__check_id(category=category)
            keys = self.__temps["keys"][category]
            complete = [complete for complete in self.__temps["complete"][category].values()] if category in self.__temps["complete"] else []

            for key in keys:
                if key not in complete and obj[key] == "Null":
                    raise KeyNull(key)

            self.__datas[category].append(obj)
            self.__temps["temp_category"] = self.temp_category = category
            print(tabulate(self.__datas[category], headers="keys"))
        else:
            raise KeyError(f"Error Category: [{category}]! --create_obj--")

    def create_attribute(self,attributes,category=None):
        category = self.temp_category if category is None or category == "" else category
        if category in self.__temps["category"]:
            attributes = normalize_attribute(category=category, attributes=attributes)

            if attributes["complete"][category]:
                key = "".join([item for item in attributes["complete"][category].keys()])
                for item in self.__datas[category]:
                    if key not in item:
                        item[key] = format(format=attributes["complete"][category]["".join([item for item in attributes["complete"][category].keys()])][key])
            elif const is not None:
                key = "".join([item for item in const[category].keys()])
                if category in self.__temps["constants"]:
                    self.__temps["constants"][category].update(const[category])
                else:
                    self.__temps["constants"][category] = const[category]
                for item in self.__datas[category]:
                    if key not in item:
                        item[key] = format(format=const["".join([item for item in const.keys()])][key])
            else:
                raise KeyError("Unknown Error! --create_attribute--")

    def create_key(self, key, category=None):
        category = self.temp_category if category is None or category == "" else category
        if category in self.__temps["category"]:
            if category not in self.__temps["keys"]:
                self.__temps["keys"][category] = [key]
                print(f"Key: [{key}] Successful Created")
            else:
                if key not in self.__temps["keys"][category]:
                    self.__temps["keys"][category].append(key)
                    print(f"Key: [{key}] Successful Created")
                else:
                    raise KeyError(f"This Key: [{category}] Already Exist! --create_key--")
        else:
            raise KeyError(f"Unknown Category: [{category}]! --create_key--")

    def create_const(self, constant, category=None):
        category = self.temp_category if category is None or category == "" else category
        if category in self.__temps["category"]:
            pre_const = [const.split(":=") for const in constant.split(" ")][0]
            types = [item for item in self.__temps["types"][category]]
            const = {pre_const[0]: pre_const[1]}
            if category in self.__temps["constants"]:
                if pre_const[0] in types and pre_const[0] not in self.__temps["constants"][category]:
                    self.__temps["constants"][category].update(const)
                else:
                    raise KeyError(f"This Const: [{const}] Already Exist OR Not Found In Types! --create_const--")
            else:
                if pre_const[0] in types:
                    self.__temps["constants"][category] = const
                else:
                    raise KeyError(f"This Const: [{const}] Not Found In Types! --create_const--")
        else:
            raise KeyError(f"Unknown Category: [{category}]! --create_const--")

    def create_complete(self, complete, category=None):
        category = self.temp_category if category is None or category == "" else category
        if category in self.__temps["category"]:
            pre_complete = [complete.split(":=") for complete in complete.split(" ")][0]
            types = [item for item in self.__temps["complete"][category]]
            complete = {pre_complete[0]: pre_complete[1]}
            if category in self.__temps["complete"]:
                if pre_complete[0] not in types:
                    self.__temps["complete"][category].update(complete)
                else:
                    raise KeyError(f"This Complete: [{complete}] Already Exist OR Not Found In Types! --create_complete--")
            else:
                if pre_complete[0] in types:
                    self.__temps["complete"][category] = complete
                else:
                    raise KeyError(f"This Complete: [{complete}] Not Found In Types! --create_complete--")
        else:
            raise KeyError(f"Unknown Category: [{category}]! --create_complete--")

    # ===================| Func-Chang |=================== #

    def change_obj(self,obj_id,attributes,category=None):
        category = self.temp_category if category is None or category == "" else category
        keys = create_id_list(obj_id)
        keys = {key:key for key in keys}
        if category in self.__temps["category"]:
            change = dict([attribute.split(":=") for attribute in attributes.split(" ")])
            const = self.__temps["constants"][category] if category in self.__temps["constants"] else None
            res = list({item for item in change.keys()}.intersection({item for item in const.keys()})) if const is not None else None
            if len(res) == 0:
                for item in self.__datas[category]:
                    if item["id"] in keys:
                        for key in [item for item in change.keys()]:
                            if key in item:
                                print("".join([item for item in change.keys()]))
                                item[key] = change[key]
                        del keys[item["id"]]
            else:
                raise ConstantError(res[0])
            self.temp_category = category
        else:
            raise KeyError(f"Category: [{category}] Not Found!")

    # ===================| Func-Clear |=================== #

    def clear_category(self,category=None):
        category = self.temp_category if category is None or category == "" else category
        if category in self.__temps["category"]:
            self.__datas[category].clear()
            self.temp_category = None
            print(f"Category: [{category}] Successful Clear")
        else:
            raise KeyError(f"Category: [{category}] Not Found!")

    def clear_obj(self,obj_id,category=None,index=0):
        category = self.temp_category if category is None or category == "" else category
        if category in self.__temps["category"]:
            for obj in self.__datas[category]:
                if obj["id"] == obj_id:
                    complete = self.__temps["complete"][category] if category in self.__temps["complete"] else None
                    pre_obj = {"id":obj["id"]}
                    types_obj = convert_format(self.__temps["types"][category].copy())
                    obj = normalize_obj(pre_obj, types_obj, complete) if complete is not None else normalize_obj(pre_obj,types_obj)
                    self.__datas[category][index] = obj
                    print(f"Obj [id:{obj['id']} | title:{obj['title']}] Successful Clear")
                else:
                    index += 1
        else:
            raise KeyError(f"Category: [{category}] Not Found!")

    # ===================| Func-Del |===================== #

    def del_category(self,category):
        category = self.temp_category if category is None or category == "" else category
        print(category in [key for key in self.__temps["complete"].keys()])
        for temp in self.__temps:
            if type(self.__temps[temp]) is dict and category in self.__temps[temp]:
                del self.__temps[temp][category]
            elif type(self.__temps[temp]) is list and category in self.__temps[temp]:
                self.__temps[temp].remove(category)
        del self.__datas[category]

    def del_obj(self,obj_id,category=None):
        category = self.temp_category if category is None or category == "" else category
        keys = create_id_list(obj_id)
        keys = {key: key for key in keys}
        index = 0
        if category in self.__temps["category"]:
            for item in self.__datas[category]:
                if item["id"] in keys:
                    if category in self.__free_id:
                        self.__free_id[category].add(item["id"])
                    else:
                        self.__free_id[category] = {item["id"]}
                    del self.__datas[category][index]
                    del keys[item["id"]]
                index += 1
            self.temp_category = category
        else:
            raise KeyError(f"Category: [{category}] Not Found!")

    def del_key(self,key,category=None,index=0):
        category = self.temp_category if category is None or category == "" else category
        if category in self.__temps["keys"]:
            if key in self.__temps["keys"][category]:
                for category_key in self.__temps["keys"][category]:
                    if category_key == key:
                        del self.__temps["keys"][category][index]
                        if len(self.__temps["keys"][category]) == 0:
                            del self.__temps["keys"][category]
                    else:
                        index += 1
            else:
                raise KeyError(f"Key: [{key}] Not Found!")
        else:
            raise KeyError(f"Category: [{category}] Not Found!")

    def del_const(self,constant,category=None):
        category = self.temp_category if category is None or category == "" else category
        if category in self.__temps["constants"]:
            if constant in self.__temps["constants"][category]:
                del self.__temps["constants"][category][constant]
                if len(self.__temps["constants"][category]) == 0:
                    del self.__temps["constants"][category]
            else:
                raise KeyError(f"Const: [{constant}] Not Found!")
        else:
            raise KeyError(f"Category: [{category}] Not Found!")

    def del_complete(self,complete,category=None):
        category = self.temp_category if category is None or category == "" else category
        if category in self.__temps["complete"]:
            if complete in self.__temps["complete"][category]:
                del self.__temps["complete"][category][complete]
                if len(self.__temps["complete"][category]) == 0:
                    del self.__temps["complete"][category]
            else:
                raise KeyError(f"Complete: [{complete}] Not Found!")
        else:
            raise KeyError(f"Category: [{category}] Not Found!")

    # ==================| Func-Different |===================#

    def get_datas(self,category=None):
        category = self.temp_category if category is None or category == "" else category
        if category in self.__temps["category"]:
            return self.__datas[category]
        elif category is None or category == "":
            return self.__datas
        else:
            raise KeyError(f"Category: [{category}] Not Found!")

    def print_datas(self,category=None):
        category = self.temp_category if category is None or category == "" else category
        print(self.__temps)
        if category in self.__temps["category"]:
            print(tabulate(self.__datas[category], headers="keys"))
        elif category is None or category == "":
            for category in self.__datas:
                print(tabulate(self.__datas[category],headers="keys"))
        else:
            raise KeyError(f"Category: [{category}] Not Found!")
