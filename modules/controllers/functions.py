from os import remove, makedirs
from os.path import abspath, exists, getsize
from json import dump, load
from ..errors.Errors import NotFoundError
import datetime


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
    if date_type == "date()":
        return _date_format_current()
    elif date_type == "time()":
        return _time_format_current()
    elif date_type == "datetime()":
        return _datetime_format_current()
    return "null"


def trim(text:str) -> str:
    return " ".join(text.split())


def lower(text:str) -> str:
    return text.lower()


def command(text:str) -> str:
    return lower(trim(text))


def load_datas(path:str, file_name:str | None = None, file_format:str | None = None):
    try:
        if all([file_name, file_format]):
            with open(f"{path}\\{file_name}.{file_format}", "r") as file:
                return load(file)
        else:
            with open(path, "r") as file:
                return load(file)
    except FileNotFoundError:
        raise NotFoundError(value=path, function_name="load datas")


def find_path(path:str): return exists(path)


def alias(path:str): return abspath(path)


def write_datas(datas:dict, path:str, file_name:str | None = None, file_format:str | None = None):
    try:
        if all([file_name, file_format]):
            with open(f"{path}\\{file_name}.{file_format}", "w") as file:
                dump(datas, file, indent=None, separators=(",",":"), ensure_ascii=False)
        else:
            with open(path, "w") as file:
                dump(datas, file, indent=None, separators=(",",":"), ensure_ascii=False)
    except FileNotFoundError:
        raise NotFoundError(value=path, function_name="write datas")


def create_file(folder_directory:str, file_name:str, file_format:str):
    try:
        with open(f"{folder_directory}\\{file_name}.{file_format}", "w") as file:
            file.write("{}")
    except FileNotFoundError:
        print("Error")


def create_json(folder_directory:str,file_name:str): write_datas(path=f"{folder_directory}\\{file_name}.json", datas={})


def delete_json(folder_directory:str,file_name:str): remove(f"{folder_directory}\\{file_name}")


def create_folder(folder_directory:str,folder_name:str):
    try:
        makedirs(f"{folder_directory}\\{folder_name}")
    except FileNotFoundError:
        raise NotFoundError(value=folder_name, function_name="create folder")


def category_find(new_category:str, old_category:str):
    return trim(lower(new_category)) if new_category else old_category
