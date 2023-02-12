import datetime


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
            case _: format[key] = "NaN"
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
            else: types[key] = "NaN"
        else:
            if auto_complete is not None and key in auto_complete and key != "id":
                types[key] = auto_complete[key]
            else:
                types[key] = "NaN"
    return types

