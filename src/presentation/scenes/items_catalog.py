import aiogram

from aiogram import filters, types
from aiogram.fsm import scene, context
from dependency_injector.wiring import inject, Provide

from src.core import UserSession
from src.infrastructure.services import Translator
from src.presentation import tools
from src.container import Container

class MainScene(scene.Scene):

    @scene.on.message.enter(Translator)
    @scene.on.callback_query.enter(Translator)
    @inject
    @tools.request_handler(auth=True, bypass_if_command=True)
    async def default_handler(self, query: types.CallbackQuery or types.Message, translator: Translator = Provide[Container.translator], user: UserSession=None):
        text = translator.translate("items_catalog-text")
        keyboard = [
            [
                types.InlineKeyboardButton(text="🐳  Меню", callback_data="None"),
                types.InlineKeyboardButton(text="📝  Поиск", callback_data="None"),
            ],
            [
                types.InlineKeyboardButton(text="📼  Фильтр", callback_data="None"),
                types.InlineKeyboardButton(text="📼  Сбросить фильтр", callback_data="None"),
            ],
            [
                types.InlineKeyboardButton(text="🗺  Подробнее о точках", callback_data="None"),
            ]
        ]

        return {"text": text, "reply_markup": types.InlineKeyboardMarkup(inline_keyboard=keyboard)}
