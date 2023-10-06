from modules.controllers.functions import trim, lower, date_format
from functools import reduce


def _normalize_attribute_keys(attributes:str | list) -> list:
    if type(attributes) == str:
        attributes = [item.split(":") for item in attributes.split(" ")]
    return list(filter(lambda value: value,list(map(lambda item: item[0][1:] if item[0].find("!") != -1 else None, attributes))))


def _normalize_attribute_templates(attributes:str | list) -> dict:
    if type(attributes) == str:
        attributes = [item.split(":") for item in attributes.split(" ")]
    return reduce(lambda acc,value: dict(acc, **value),[{elem[0]:elem[1].split("=")[1]} for elem in attributes if elem[1].find("=") != -1])


def _normalize_attribute_constants(attributes:str | list) -> list:
    if type(attributes) == str:
        attributes = [item.split(":") for item in attributes.split(" ")]
    return list(filter(lambda value: value,list(map(lambda item: item[0][1:] if item[0].find("$") != -1 else None, attributes))))


def _normalize_attribute_types(attributes:str | list) -> dict:
    types = dict()
    if type(attributes) is str:
        attributes = [item.split(":") for item in attributes.split(" ")]
    for item in attributes:
        key = item[0].split("!")[1] if "!" in item[0] else item[0].split("=")[0] if "=" in item[1] else item[0].split("$")[1] if "$" in item[1] else item[0]
        key_type = item[1].split("=")[0] if "=" in item[1] else item[1]
        types[key] = key_type
    return types


def _normalize_all_attributes(attributes:str | list) -> dict:
    keys = _normalize_attribute_keys(attributes)
    templates = _normalize_attribute_templates(attributes)
    consts = _normalize_attribute_constants(attributes)
    types = _normalize_attribute_types(attributes)

    return {"keys": keys, "templates": templates, "constants": consts, "types": types}


def _normalize_obj_types(obj_type) -> dict:
    glob_types = {"int":int, "float":float, "str":str, "list":list, "dict":dict, "tuple":tuple, "bool":bool, "date":"date", "time":"time"}
    return reduce(lambda acc,value: dict(acc, **value),[{key:glob_types[item]} for key,item in obj_type.items() if item in glob_types])


def _normalize_obj_attribute(attributes: dict, obj_template:dict, auto_complete:list | None = None) -> dict:
    obj_keys = list(obj_template.keys())

    for key in obj_keys:
        if key in attributes:
            obj_type = obj_template[key]
            if obj_type in [int, float, str]:
                obj_template[key] = attributes[key]
            elif obj_type is list:
                obj_template[key] = attributes[key].split(",")
            elif obj_type is dict:
                obj_template[key] = reduce(lambda acc,value: dict(acc, **value),[{elem.split(">")[0]:elem.split(">")[1]} for elem in attributes[key].split(",")])
            elif obj_type is tuple:
                obj_template[key] = tuple(attributes[key].split(","))
            elif obj_type is bool:
                obj_template[key] = bool(attributes[key])
            else:
                obj_template[key] = "undefined"
        elif key in auto_complete:
            obj_template[key] = date_format(auto_complete[key]) if key == "date" else auto_complete[key]
        else:
            obj_template[key] = "undefined"

    return obj_template


def normalize_attribute(category: str, attributes: str) -> dict:
    if "title" not in attributes:
        attributes = "title:str=undefined " + attributes
    if "id" not in attributes:
        attributes = "id:int " + attributes
    attributes = trim(lower(attributes))

    attributes = [item.split(":") for item in attributes.split(" ")]

    return _normalize_all_attributes(attributes=attributes)


def normalize_obj(attributes:str | dict, types:str | dict, auto_complete:list | None = None) -> dict:
    if type(attributes) is str and len(attributes) == 0:
        attributes = {}
    if type(attributes) is not dict:
        attributes = dict([attribute.split("=") for attribute in trim(lower(attributes)).split(" ")])
    obj_template = _normalize_obj_types(types)
    return _normalize_obj_attribute(attributes, obj_template, auto_complete)
