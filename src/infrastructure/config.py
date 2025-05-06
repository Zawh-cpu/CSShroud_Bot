import json

class AiConfig:
    def __init__(self, **kwargs):
        self.TOKEN = kwargs.get('TOKEN', "")
        self.BASE_MODEL = kwargs.get('BASE_MODEL', "")
        self.BASE_URL = kwargs.get("BASE_URL", "AAAAA")
        self.TOKEN_LIMIT = kwargs.get('TOKEN_LIMIT', 1)
        if self.TOKEN_LIMIT > 1000:
            self.TOKEN_LIMIT = 1000
        elif self.TOKEN_LIMIT < 1:
            self.TOKEN_LIMIT = 1
        self.MAX_RETRIES = kwargs.get('MAX_RETRIES', 3)

    def dump(self):
        return self.__dict__

class Config:
    """ Singleton-класс для загрузки конфигурации из JSON. """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance._load_config()
        return cls._instance

    def _load_config(self):
        with open("config.json", "r") as file:
            data = json.load(file)
            self.BASE_URL = data.get("BASE_URL", "")
            self.API_KEY = data.get("API_KEY", "")
            self.BOT_TOKEN = data.get("BOT_TOKEN", "")
            self.REDIS_HOST = data.get("REDIS_HOST", "localhost")
            self.REDIS_PORT = data.get("REDIS_PORT", 1000)
            self.REDIS_DB = data.get("REDIS_DB", 0)
            self.LANGUAGES_FOLDER = data.get("LANGUAGES_FOLDER", "src/infrastructure/localization")
            self.AI = AiConfig(**data.get("AI", dict()))

        self.save_config()

    def save_config(self):
        with open("config.json", "w") as file:
            file.write(json.dumps({
                "BASE_URL": self.BASE_URL,
                "API_KEY": self.API_KEY,
                "BOT_TOKEN": self.BOT_TOKEN,
                "REDIS_HOST": self.REDIS_HOST,
                "REDIS_PORT": self.REDIS_PORT,
                "REDIS_DB": self.REDIS_DB,
                "LANGUAGES_FOLDER": self.LANGUAGES_FOLDER,
                "AI": self.AI.dump()
            }, indent=4))
