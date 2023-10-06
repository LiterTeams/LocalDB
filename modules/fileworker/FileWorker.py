from ..controllers.functions import load_datas, alias
from ..errors.Errors import InitializationError, NotFoundError


class JsonFileWorker:
    def __init__(self):
        self.__jfw_config_dir = alias("assets\\private\\config")
        self.__config_format = "json"
        self.__configs_name = list()
        self.__configs:dict = dict()
        self.__version:str = ""
        self.__status = False

    def __config_init(self) -> None:
        data = load_datas(f"{self.__jfw_config_dir}\\fileworker.config.{self.__config_format}")
        self.__configs_name += data["configs_name"]
        self.__version = data["version"]
        for config_name in self.__configs_name:
            try:
                self.__configs[config_name] = load_datas(f"{self.__jfw_config_dir}\\{config_name}.{self.__config_format}")
            except Exception:
                raise InitializationError(value=config_name, function_name="JsonFileWorker - config init")
        self.__status = True

    def start(self):
        self.__config_init()

    def get_config_key(self, config_key:str):
        configs = [key for key in self.__configs.keys()]
        if config_key not in configs:
            raise NotFoundError(value=config_key, function_name="Json File Worker - get config key")
        return self.__configs[config_key]

    @property
    def version(self) -> str: return self.__version

    @property
    def status(self) -> bool: return self.__status
