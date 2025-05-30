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

from .users_list import UsersList
from .manage_user import ManageUserScene
from .delete import DeleteScene
from .set_role import SetRoleScene
from .set_rate import SetRateScene
from .set_rate_select_time import SetRateTimeScene


category = "admin_panel"


class MainScene(tools.Scene, state="admin_panel"):

    @scene.on.message.enter()
    @scene.on.callback_query.enter()
    @tools.request_handler(auth=True, bypass_if_command=True, category=category)
    @inject
    async def default_handler(self, query: types.CallbackQuery or types.Message,
                              translator: Translator = Provide[Container.translator], user: UserSession = None):
        keyboard = [
            [types.InlineKeyboardButton(text=translator.translate("ui-tag-menu"),
                                        callback_data="menu")],
            [types.InlineKeyboardButton(text=translator.translate("ui-tag-admin_panel-users"),
                                        callback_data="users")]
        ]

        return {"reply_markup": types.InlineKeyboardMarkup(inline_keyboard=keyboard)}

    @scene.on.callback_query(aiogram.F.data == "users")
    # @tools.request_handler(auth=False)
    async def users_list(self, query: types.CallbackQuery or types.Message, user: UserSession = None):
        await self.wizard.goto(UsersList)
