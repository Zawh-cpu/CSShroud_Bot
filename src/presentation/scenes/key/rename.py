import aiogram

from aiogram import filters, types
from aiogram.fsm import scene, context
from dependency_injector.wiring import inject, Provide

from src.core import UserSession, Key, KeyStatus
from src.infrastructure.services import Translator, ApiRepository
from src.infrastructure.services.rights_service import RightsService, Rights
from src.presentation import tools
from src.container import Container

category = "view_key"


class RenameScene(scene.Scene, state="view_key"):

    @scene.on.message.enter()
    @scene.on.callback_query.enter()
    @tools.request_handler(auth=False, category=category, state="rename")
    @inject
    async def default_handler(self, query: types.CallbackQuery or types.Message,
                              translator: Translator = Provide[Container.translator],
                              api_repository: ApiRepository = Provide[Container.api_repository],
                              user: UserSession = None):

        key_id = await self.wizard.get_value("selected_key")
        if not key_id:
            raise Exception("error-key-not-selected")

        text = translator.translate("view_key-rename-text").format(key_id=key_id)

        keyboard = [
            [
                types.InlineKeyboardButton(text=translator.translate("ui-tag-menu"), callback_data="menu"),

                types.InlineKeyboardButton(text=translator.translate("ui-tag-back"),
                                           callback_data="back"),

                types.InlineKeyboardButton(text=translator.translate("ui-tag-my_keys"), callback_data="keys")
            ]
        ]

        return {"text": text, "reply_markup": types.InlineKeyboardMarkup(inline_keyboard=keyboard)}

    @scene.on.message()
    @tools.request_handler(auth=True)
    @inject
    async def rename(self, query: types.CallbackQuery or types.Message,
                     api_repository: ApiRepository = Provide[Container.api_repository],
                     user: UserSession = None):

        key_id = await self.wizard.get_value("selected_key")
        if not key_id:
            raise Exception("error-key-not-selected")

        result = await api_repository.rename(query.text[:96], key_id, user.tokens.action_token)
        if not result.is_success():
            raise Exception("error-key-rename-aborted")

        await self.wizard.back()

    @scene.on.callback_query(aiogram.F.data == "back")
    async def back(self, query: types.CallbackQuery or types.Message):

        await self.wizard.back()