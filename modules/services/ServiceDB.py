

class ServiceDB:
    def __init__(self):
        self.lite_db = None
        self.mongo_bd = None
        self.mysql_db = None
        self.postgres_db = None
        self.sqllite_db = None

    def __config_init(self, config): ...

    def start(self, config): ...
