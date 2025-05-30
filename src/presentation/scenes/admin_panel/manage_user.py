import aiogram
import math

from aiogram import filters, types
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm import scene, context
from dependency_injector.wiring import inject, Provide

from src import ApiRepository, PatchUserDto
from src.core import UserSession
from src.infrastructure.services import Translator
from src.presentation import tools
from src.container import Container
from src.infrastructure.services.rights_service import RightsService, Rights
from src.application import dtos

from .delete import DeleteScene
from .set_role import SetRoleScene
from .set_rate import SetRateScene

category = "admin_panel"


class ManageUserScene(tools.Scene, state="admin_panel-users-manage"):
    @scene.on.message.enter()
    @scene.on.callback_query.enter()
    @tools.request_handler(auth=True, category=category, state="m_user")
    @inject
    async def default_handler(self, query: types.CallbackQuery or types.Message,
                              translator: Translator = Provide[Container.translator],
                              api_repository: ApiRepository = Provide[Container.api_repository],
                              user: UserSession = None):

        if not RightsService.has_access(user.data.role.permissions, Rights.AdminAccess):
            raise Exception("error-permission_denied")

        selected_user = (await self.wizard.get_data()).get("selected_user")
        if not selected_user:
            raise Exception("error-user_not_selected")

        user_dto: dtos.Result = await api_repository.get_user_by_id_info_async(selected_user, user.tokens.action_token)
        print(selected_user, user_dto)
        if not user_dto.is_success():
            raise Exception("error-user_invalid")

        text = translator.translate("profile-text").format(id=user_dto.value.id,
                                                           nickname=user_dto.value.nickname,
                                                           login=user_dto.value.login,
                                                           role_name=translator.translate(
                                                               f"role-{user_dto.value.role.name}"),
                                                           rate_name=translator.translate(
                                                               f"rate-{user_dto.value.rate.name}", ),
                                                           payed_until=user_dto.value.payed_until if user_dto.value.payed_until else "➖",
                                                           created_at=translator.date_to_text(
                                                               user_dto.value.created_at),
                                                           verification_status="✅" if user_dto.value.is_verified else "➖")
        keyboard = [
            [types.InlineKeyboardButton(text=translator.translate("ui-tag-menu"), callback_data="menu"),
             types.InlineKeyboardButton(text=translator.translate("ui-tag-back"),
                                        callback_data="back")],
            [types.InlineKeyboardButton(text=translator.translate("ui-tag-admin_panel-user-delete"),
                                        callback_data=tools.OptSelector(i=user_dto.value.id, o="del").pack())],
            [types.InlineKeyboardButton(text=translator.translate("ui-tag-admin_panel-user-check-off"),
                                        callback_data=tools.OptSelector(i=user_dto.value.id, o="c-off").pack())
             if user_dto.value.is_verified else
             types.InlineKeyboardButton(text=translator.translate("ui-tag-admin_panel-user-check-on"),
                                        callback_data=tools.OptSelector(i=user_dto.value.id, o="c-on").pack())
             ],
            [types.InlineKeyboardButton(text=translator.translate("ui-tag-admin_panel-user-set_role"),
                                        callback_data=tools.OptSelector(i=user_dto.value.id, o="rol").pack()),
             types.InlineKeyboardButton(text=translator.translate("ui-tag-admin_panel-user-set_rate"),
                                        callback_data=tools.OptSelector(i=user_dto.value.id, o="rat").pack())]
        ]

        return {"text": text, "category_args": (translator.key_short_id(selected_user),), "reply_markup": types.InlineKeyboardMarkup(inline_keyboard=keyboard)}

    @scene.on.callback_query(tools.OptSelector.filter(aiogram.F.o == "del"))
    async def delete(self, query: types.CallbackQuery or types.Message, callback_data: tools.OptSelector,
                     user: UserSession = None):

        await self.wizard.update_data({"selected_user": callback_data.i})
        await self.wizard.goto(DeleteScene)

    @scene.on.callback_query(tools.OptSelector.filter(aiogram.F.o == "rol"))
    async def set_role(self, query: types.CallbackQuery or types.Message, callback_data: tools.OptSelector,
                     user: UserSession = None):

        await self.wizard.update_data({"selected_user": callback_data.i})
        await self.wizard.goto(SetRoleScene)

    @scene.on.callback_query(tools.OptSelector.filter(aiogram.F.o == "rat"))
    async def set_rate(self, query: types.CallbackQuery or types.Message, callback_data: tools.OptSelector,
                     user: UserSession = None):

        await self.wizard.update_data({"selected_user": callback_data.i})
        await self.wizard.goto(SetRateScene)

    @scene.on.callback_query(tools.OptSelector.filter(aiogram.F.o == "c-on"))
    @tools.request_handler(auth=True)
    @inject
    async def check_on(self, query: types.CallbackQuery or types.Message, callback_data: tools.OptSelector,
                       api_repository: ApiRepository = Provide[Container.api_repository],
                       user: UserSession = None):

        if (await api_repository.user_patch_async(callback_data.i, PatchUserDto(is_verified=True),
                                                  user.tokens.action_token)).is_success():
            await self.wizard.retake()

    @scene.on.callback_query(tools.OptSelector.filter(aiogram.F.o == "c-off"))
    @tools.request_handler(auth=True)
    @inject
    async def check_off(self, query: types.CallbackQuery or types.Message, callback_data: tools.OptSelector,
                        api_repository: ApiRepository = Provide[Container.api_repository],
                        user: UserSession = None):

        if (await api_repository.user_patch_async(callback_data.i, PatchUserDto(is_verified=False),
                                                  user.tokens.action_token)).is_success():
            await self.wizard.retake()
