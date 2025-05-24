import aiogram
import math

from aiogram import filters, types
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm import scene, context
from dependency_injector.wiring import inject, Provide

from src import ApiRepository
from src.core import UserSession
from src.infrastructure.services import Translator
from src.presentation import tools
from src.container import Container
from src.infrastructure.services.rights_service import RightsService, Rights
from src.application import dtos

from .manage_user import ManageUserScene

category = "admin_panel"


class UsersList(tools.PageScene, state="admin_panel-users"):
    _data_label = "selected_user"
    _next = ManageUserScene

    @scene.on.message.enter()
    @scene.on.callback_query.enter()
    @tools.request_handler(auth=True, bypass_if_command=True, category=category)
    @inject
    async def default_handler(self, query: types.CallbackQuery or types.Message,
                              translator: Translator = Provide[Container.translator], api_repository: ApiRepository = Provide[Container.api_repository], user: UserSession = None):
        if not RightsService.has_access(user.data.role.permissions, Rights.AdminAccess):
            raise Exception("permission-error")

        page = (await self.wizard.get_value("page")) or 0
        users_dto: dtos.Result = await api_repository.get_users(user.tokens.action_token, page=page, size=10)
        if not users_dto.is_success():
            raise Exception("error-unknown")
        max_pages = math.ceil(users_dto.value.users_count / 10)
        if max_pages < 1:
            max_pages = 1

        keyboard = [
            [
                types.InlineKeyboardButton(text=translator.translate("ui-tag-menu"),
                                           callback_data="menu"),
                types.InlineKeyboardButton(text=translator.translate("ui-tag-back"),
                                           callback_data="admin"),
            ],
            *[[types.InlineKeyboardButton(
                text=f"({"🎖️" if usr.is_verified else "🔴"})  #{translator.key_short_id(usr.id)} | {usr.nickname} [TG:{usr.telegram_id}]",
                callback_data=tools.Selector(i=str(usr.id)).pack())] for usr in users_dto.value.users],
            [
                types.InlineKeyboardButton(text="◀️", callback_data="--page" if page > 0 else "None"),
                types.InlineKeyboardButton(text=f"{page + 1} / {max_pages}", callback_data="None"),
                types.InlineKeyboardButton(text="▶️", callback_data="++page" if page < max_pages - 1 else "None"),
            ]
        ]

        return {"reply_markup": types.InlineKeyboardMarkup(inline_keyboard=keyboard)}