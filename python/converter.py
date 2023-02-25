import datetime
from functools import reduce


def format(format,value=None):
    match format:
        case "List()":
            if "," in value:
                return value.split(",")
            else:
                return [value]
        case "Date()":
            date = str(datetime.datetime.now()).split(".")[0]
            return date
        case "this.Date()": pass
        case "Time()":
            if value.startswith("."):
                value = int(float(value)*100) if len(value) < 2 else int(float(value)*int("1"+"0"*(len(value)-1)))
                if 0 <= value <= 59:
                    return f"{value} Sec"
                else:
                    return f"{int(value/60)} Mn"
            elif 0 <= int(value) <= 59:
                return f"{value} Mn"
            else:
                return f"{round(int(value)/60,1)} Hr"

        case "Money()": pass
        case _: raise KeyError("Format Error!")


def convert_format(format):
    for key in format:
        match format[key]:
            case "str": format[key] = str
            case "int": format[key] = int
            case "float": format[key] = float
            case "list": format[key] = list
            case "dict": format[key] = dict
            case "time": format[key] = "time"
            case "date": format[key] = "date"
            case "href": format[key] = "href"
            case "nan": format[key] = "NaN"
            case _: format[key] = "Null"
    return format


def normalize_obj(obj,types,auto_complete=None):
    for key in types:
        if key in obj:
            if types[key] is str: types[key] = obj[key]
            elif types[key] is int: types[key] = obj[key]
            elif types[key] is float: types[key] = obj[key]
            elif types[key] is list: types[key] = format(format="List()",value=obj[key])
            elif types[key] is dict: types[key] = obj[key]
            elif types[key] == "data": types[key] = format(format="Date()",value=obj[key])
            elif types[key] == "time": types[key] = format(format="Time()",value=obj[key] if obj[key] != "" else 0)
            elif types[key] == "money": types[key] = obj[key]
            elif types[key] == "NaN": types[key] = obj[key]
            else: types[key] = "Null"
        else:
            if auto_complete is not None and key in auto_complete and key != "id":
                types[key] = auto_complete[key]
            else:
                types[key] = "Null"
    return types


def normalize_attribute(category: str, attributes: str) -> dict:
    attributes = "@title[unknown-title]:=str " + attributes if "title" not in attributes else None
    attributes = "id:=int " + attributes if "id" not in attributes else None
    attributes = [item.split(":=") for item in attributes.split(" ")]
    pre_keys = list(map(lambda item: [elem.split("!")[1] for elem in item if elem.startswith("!")], attributes))
    pre_complete = list(map(lambda item: [elem.split("@")[1] for elem in item if elem.startswith("@")], attributes))
    pre_const = list(map(lambda item: [elem.split("$")[1] for elem in item if elem.startswith("$")], attributes))
    keys = {category: tuple([elem[0] for elem in pre_keys if len(elem) > 0])} if len([elem[0] for elem in pre_keys if len(elem) > 0]) > 0 else None
    complete = {category: reduce(lambda x, y: dict(x, **y),[{elem[0].split("[")[0]: elem[0].split("[")[1].split("]")[0]} for elem in pre_complete if len(elem) > 0])} if len([{elem[0].split("[")[0]: elem[0].split("[")[1].split("]")[0]} for elem in pre_complete if len(elem) > 0]) > 0 else None
    const = {category: [elem[0] for elem in pre_const if len(elem) > 0]} if len([elem[0] for elem in pre_const if len(elem) > 0]) > 0 else None

    types = dict()
    for item in attributes:
        if "!" in item[0]:
            key = item[0].split("!")[1]
            types[key] = item[1]
        elif "@" in item[0]:
            key = item[0].split("@")[1].split("[")[0]
            types[key] = item[1]
        elif "$" in item[0]:
            key = item[0].split("$")[1]
            types[key] = item[1]
        else:
            types[item[0]] = item[1]

    normalize = {"keys":keys, "complete":complete, "constants":const, "types":types}
    return normalize
