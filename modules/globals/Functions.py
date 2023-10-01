import os
import datetime
import json


def trim(text:str) -> str:
    return " ".join(text.split())


def lower(text:str) -> str:
    return text.lower()


def command(text:str) -> str:
    return lower(trim(text))


def _date_format_current() -> str:
    date = str(datetime.date.today()).split("-")
    return f"{date[2]}-{date[1]}-{date[0]}"


def _time_format_current() -> str:
    time = str(datetime.datetime.now().time()).split(".")[0].split(":")
    return f"{int(time[0])}:{time[1]} {'am' if 0 <= int(time[0]) <= 11 else 'pm'}"


def _datetime_format_current() -> str:
    date = _date_format_current()
    time = _time_format_current()
    return f"{date} | {time}"


def date_format(date_type:str):
    if date_type == "Date()":
        return _date_format_current()
    elif date_type == "Time()":
        return _time_format_current()
    elif date_type == "DateTime()":
        return _datetime_format_current()
    return "null"


def load_datas(path:str):
    with open(path, "r") as file:
        return json.load(file)


def find_path(path:str):
    return os.path.exists(path)


def write_datas(path:str, datas:dict):
    with open(path, "w") as file:
        json.dump(datas, file, indent=2, ensure_ascii=False)


def create_json(folder_directory:str,file_name:str):
    path = f"{folder_directory}/{file_name}.json"
    write_datas(path=path, datas={})


def create_folder(folder_directory:str,folder_name:str):
    os.makedirs(f"{folder_directory}/{folder_name}")


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
