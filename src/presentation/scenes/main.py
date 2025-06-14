import aiogram

from aiogram import filters, types
from aiogram.fsm import scene, context
from dependency_injector.wiring import inject, Provide

from src.core import UserSession
from src.infrastructure.services import Translator
from src.infrastructure.services.rights_service import RightsService, Rights
from src.presentation import tools
from src.container import Container

class MainScene(scene.Scene, reset_data_on_enter=False, reset_history_on_enter=True, callback_query_without_state=True):

    @scene.on.message.enter(Translator)
    @scene.on.callback_query.enter(Translator)
    @tools.request_handler(auth=True, bypass_if_command=True, category="menu")
    @inject
    async def default_handler(self, query: types.CallbackQuery or types.Message, translator: Translator = Provide[Container.translator], user: UserSession=None):
        # print("main -> user", user)
        # print("main -> user -> data", user.data)
        # print("main -> user -> data -> role", user.data.role)

        text = translator.translate("menu-text")
        keyboard = [
            [types.InlineKeyboardButton(text=translator.translate("ui-tag-profile"), callback_data="profile"),
             types.InlineKeyboardButton(text=translator.translate("ui-tag-settings"), callback_data="settings")],
            [types.InlineKeyboardButton(text=translator.translate("ui-tag-rates"),
                                        callback_data="rate")],
            [types.InlineKeyboardButton(text=translator.translate("ui-tag-my_keys"), callback_data="keys")],
            [types.InlineKeyboardButton(text=translator.translate("ui-tag-how_to_use"), callback_data="how_to_use")],
        ]

        if RightsService.has_access(user.data.role.permissions, Rights.AdminAccess):
            keyboard.append([
                types.InlineKeyboardButton(text=translator.translate("ui-tag-admin_panel"), callback_data="admin"),
            ])

        return {"text": text, "reply_markup": types.InlineKeyboardMarkup(inline_keyboard=keyboard)}
