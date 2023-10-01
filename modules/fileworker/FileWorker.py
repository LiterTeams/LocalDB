from os.path import abspath as alias
from modules.globals.Functions import load_datas
from modules.globals.Errors import InitializationError


class JsonFileWorker:
    def __init__(self):
        self.__jfw_config_dir = alias("assets/config")
        self.__config_format = "json"
        self.__configs_name = list()
        self.__configs:dict = dict()
        self._status = False

    def __config_init(self) -> None:
        self.__configs_name.append(load_datas(f"{self.__jfw_config_dir}\\fileworker.config.{self.__config_format}")["configs_name"][0])
        for config_name in self.__configs_name:
            try:
                self.__configs[config_name] = load_datas(f"{self.__jfw_config_dir}\\{config_name}.{self.__config_format}")
            except Exception:
                raise InitializationError(value=config_name, function_name="JsonFileWorker - config init")
        self._status = True

    def start(self):
        self.__config_init()

    def get_config_key(self, config_key:str):
        if config_key in [key for key in self.__configs.keys()]:
            return self.__configs[config_key]
