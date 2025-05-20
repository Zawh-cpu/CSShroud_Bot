import aiogram

from aiogram import types
from aiogram.fsm import scene
from dependency_injector.wiring import inject, Provide

from src.core import UserSession
from src.infrastructure.services import Translator
from src.presentation import tools
from src.container import Container

category = "view_key"


class AppsToConnect(scene.Scene, state="view_key-apps"):

    @scene.on.message.enter()
    @scene.on.callback_query.enter()
    @tools.request_handler(auth=False, category=category, state="apps")
    @inject
    async def default_handler(self, query: types.CallbackQuery or types.Message,
                              translator: Translator = Provide[Container.translator],
                              user: UserSession = None):

        key_id = await self.wizard.get_value("selected_key")
        if not key_id:
            raise Exception("error-key-not-selected")

        text = translator.translate("view_key-apps-text")
        keyboard = [
            [
                types.InlineKeyboardButton(text=translator.translate("ui-tag-menu"), callback_data="menu"),

                types.InlineKeyboardButton(text=translator.translate("ui-tag-back"),
                                           callback_data=tools.OptSelector(i=key_id, o="back").pack()),

                types.InlineKeyboardButton(text=translator.translate("ui-tag-my_keys"), callback_data="keys")
            ]
        ]

        return {"text": text, "category_args": (translator.key_short_id(key_id),),
                "reply_markup": types.InlineKeyboardMarkup(inline_keyboard=keyboard)}

    @scene.on.callback_query(tools.OptSelector.filter(aiogram.F.o == "back"))
    async def back(self, query: types.CallbackQuery or types.Message, callback_data: tools.OptSelector):
        await self.wizard.update_data({"selected_key": callback_data.i})
        await self.wizard.back()