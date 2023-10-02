from modules.globals.Functions import date_format, trim ,lower
from functools import reduce


def _normalize_attribute_keys(category: str, attributes:str | list) -> list:
    if type(attributes) == list:
        return list(filter(lambda value: value,list(map(lambda item: item[0][1:] if item[0].find("!") != -1 else None, attributes))))
    elif type(attributes) == str:
        attributes = [item.split(":") for item in attributes.split(" ")]
        _normalize_attribute_keys(category, attributes)
    return []


def _normalize_attribute_templates(category: str, attributes:str | list) -> dict:
    if type(attributes) == list:
        return reduce(lambda acc,value: dict(acc, **value),[{elem[0]:elem[1].split("=")[1]} for elem in attributes if elem[1].find("=") != -1])
    elif type(attributes) == str:
        attributes = [item.split(":") for item in attributes.split(" ")]
        _normalize_attribute_templates(category, attributes)
    return {}


def _normalize_attribute_constants(category: str, attributes:str | list) -> list:
    if type(attributes) == list:
        return list(filter(lambda value: value,list(map(lambda item: item[0][1:] if item[0].find("$") != -1 else None, attributes))))
    elif type(attributes) == str:
        attributes = [item.split(":") for item in attributes.split(" ")]
        _normalize_attribute_constants(category, attributes)
    return []


def _normalize_attribute_types(category:str, attributes:str | list) -> dict:
    if type(attributes) is list:
        types = dict()
        for item in attributes:
            key = item[0].split("!")[1] if "!" in item[0] else item[0].split("=")[0] if "=" in item[1] else item[0].split("$")[1] if "$" in item[1] else item[0]
            key_type = item[1].split("=")[0] if "=" in item[1] else item[1]
            types[key] = key_type
        return types
    elif type(attributes) is str:
        attributes = [item.split(":") for item in attributes.split(" ")]
        _normalize_attribute_types(category, attributes)
    return {}


def _normalize_obj_types(obj_type):
    for key in obj_type:
        match obj_type[key]:
            case "int": obj_type[key] = int
            case "float": obj_type[key] = float
            case "str": obj_type[key] = str
            case "list": obj_type[key] = list
            case "dict": obj_type[key] = dict
            case "date" | "time" | "null": pass
            case _: obj_type[key] = "undefined"
    return obj_type


def normalize_attribute(category: str, attributes: str) -> dict:
    if "title" not in attributes:
        attributes = "title:str=null" + attributes
    if "id" not in attributes:
        attributes = trim(lower("id:int " + attributes))

    attributes = [item.split(":") for item in attributes.split(" ")]

    keys = _normalize_attribute_keys(category, attributes)
    templates = _normalize_attribute_templates(category, attributes)
    consts = _normalize_attribute_constants(category, attributes)
    types = _normalize_attribute_types(category, attributes)

    return {"keys": keys, "templates": templates, "constants": consts, "types": types}


def normalize_obj(attributes:str | dict, types:str | dict, auto_complete:list | None = None):
    if type(attributes) is not dict:
        attributes = dict([attribute.split("=") for attribute in trim(lower(attributes)).split(" ")])
        normalize_obj(attributes, types, auto_complete)
    else:
        types = _normalize_obj_types(types)

        for key in types:
            if key in attributes:
                if types[key] in [int,float,str,dict]:
                    types[key] = attributes[key]
                elif types[key] is list:
                    value = attributes[key]
                    types[key] = value.split(",") if "," in value else [value]
                elif types[key] == "null":
                    types[key] = attributes[key]
                else:
                    types[key] = "undefined"
            else:
                if auto_complete is not None and key in auto_complete and key != "id":
                    if types[key] == "date":
                        types[key] = date_format(auto_complete[key])
                    else:
                        types[key] = auto_complete[key]
                else:
                    types[key] = "undefined"
    return types
