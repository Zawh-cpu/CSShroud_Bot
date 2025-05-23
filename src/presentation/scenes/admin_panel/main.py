import aiogram

from aiogram import filters, types
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm import scene, context
from dependency_injector.wiring import inject, Provide

from src.presentation.tools.selector import IntSelector
from src.core import UserSession
from src.infrastructure.services import Translator
from src.infrastructure.services.rights_service import RightsService, Rights
from src.infrastructure.services.server_service import ServerService
from src.presentation import tools
from src.container import Container


category = "admin_panel"


class MainScene(tools.Scene, state="admin_panel"):

    @scene.on.message.enter()
    @scene.on.callback_query.enter()
    @tools.request_handler(auth=True, bypass_if_command=True, category=category)
    @inject
    async def default_handler(self, query: types.CallbackQuery or types.Message,
                              translator: Translator = Provide[Container.translator], server_service: ServerService = Provide[Container.server_service], user: UserSession = None):
        keyboard = [
            [types.InlineKeyboardButton(text=translator.translate("ui-tag-menu"),
                                        callback_data="menu")],
            [types.InlineKeyboardButton(text=translator.translate("ui-tag-ap-users"),
                                        callback_data="users")]
        ]

        return {"reply_markup": types.InlineKeyboardMarkup(inline_keyboard=keyboard)}

    @scene.on.callback_query(aiogram.F.data == "ap-users")
    # @tools.request_handler(auth=False)
    async def users_list(self, query: types.CallbackQuery or types.Message, user: UserSession = None):
        await self.wizard.goto(UsersList)
