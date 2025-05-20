import pathlib
import json
import functools
from datetime import datetime, timezone, timedelta


class Translator:
    _instance = None
    _lang_base: dict = dict()

    def __new__(cls, config=None):
        if cls._instance is None:
            cls._instance = super(Translator, cls).__new__(cls)
            cls._instance._load_languages(config)
        return cls._instance

    def _load_languages(self, config):
        for file in pathlib.Path().resolve().joinpath(config.LANGUAGES_FOLDER).iterdir():
            self._lang_base[file.stem] = json.load(file.open("r", encoding="utf-8"))

    @functools.cache
    def translate(self, text, lang="ru-RU"):
        return self._lang_base.get(lang, {}).get(text, text)

    @staticmethod
    def date_to_text(date: datetime, utc_offset=3):
        return date.astimezone(timezone(timedelta(hours=utc_offset))).strftime("%y/%m/%d %H:%M:%S %Z")

    @staticmethod
    def key_short_id(key_id: str):
        return key_id[4:8] + key_id[9:13]