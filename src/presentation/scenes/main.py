import aiogram

from aiogram import filters, types
from aiogram.fsm import scene, context
from dependency_injector.wiring import inject, Provide

from src.core import UserSession
from src.infrastructure.services import Translator
from src.infrastructure.services.rights_service import RightsService
from src.presentation import tools
from src.container import Container

class MainScene(scene.Scene, reset_data_on_enter=False, reset_history_on_enter=True, callback_query_without_state=True):

    @scene.on.message.enter(Translator)
    @scene.on.callback_query.enter(Translator)
    @tools.request_handler(auth=True, bypass_if_command=True)
    @inject
    async def default_handler(self, query: types.CallbackQuery or types.Message, translator: Translator = Provide[Container.translator], user: UserSession=None):
        text = await translator.translate("menu-text")
        keyboard = [
            [types.InlineKeyboardButton(text=await translator.translate("ui-tag-profile"), callback_data="profile"),
             types.InlineKeyboardButton(text=await translator.translate("ui-tag-settings"), callback_data="settings")],
            [types.InlineKeyboardButton(text=await translator.translate("ui-tag-rates"),
                                        callback_data="rates")],
            [types.InlineKeyboardButton(text=await translator.translate("ui-tag-keys_viewer"), callback_data="keys_viewer")],
            [types.InlineKeyboardButton(text=await translator.translate("ui-tag-how_to_use"), callback_data="how_to_use")],
        ]

        if RightsService.has_access(user.rights, Rights.AdminAccess):
            keyboard.append([
                types.InlineKeyboardButton(text=await translator.translate("ui-tag-admin_panel"), callback_data="admin"),
            ])

        return {"text": text, "reply_markup": types.InlineKeyboardMarkup(inline_keyboard=keyboard)}
