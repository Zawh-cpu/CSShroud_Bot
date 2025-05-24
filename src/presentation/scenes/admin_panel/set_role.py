import aiogram

from aiogram import filters, types
from aiogram.fsm import scene, context
from dependency_injector.wiring import inject, Provide

from src.application.dtos import PatchKeyDto
from src.core import UserSession, Key, KeyStatus
from src.infrastructure.services import Translator, ApiRepository, ServerService
from src.infrastructure.services.rights_service import RightsService, Rights
from src.presentation import tools
from src.container import Container

category = "admin_panel"


class SetRoleScene(scene.Scene, state="admin_panel-set_role"):

    @scene.on.message.enter()
    @scene.on.callback_query.enter()
    @tools.request_handler(auth=False, category=category, state="set_role")
    @inject
    async def default_handler(self, query: types.CallbackQuery or types.Message,
                              translator: Translator = Provide[Container.translator],
                              server_service: ServerService = Provide[Container.server_service],
                              user: UserSession = None):
        selected_user = (await self.wizard.get_data()).get("selected_user")
        if not selected_user:
            raise Exception("error-user_not_selected")

        roles = await server_service.get_roles()

        text = translator.translate("admin_panel-manage_user-set_role-text").format(id=translator.key_short_id(selected_user))

        keyboard = [
            [
                types.InlineKeyboardButton(text=translator.translate("ui-tag-menu"), callback_data="menu"),
                types.InlineKeyboardButton(text=translator.translate("ui-tag-cancel-short"),
                                           callback_data=tools.OptSelector(i=selected_user, o="back").pack()),
                types.InlineKeyboardButton(text=translator.translate("ui-tag-my_keys"), callback_data="keys")
            ],
            *[[types.InlineKeyboardButton(text=translator.translate(f"role-{role}"), callback_data=set) for role in roles]]
        ]

        return {"text": text, "category_args": (translator.key_short_id(selected_user),), "reply_markup": types.InlineKeyboardMarkup(inline_keyboard=keyboard)}

    @scene.on.callback_query(tools.Selector.filter())
    @tools.request_handler(auth=True)
    @inject
    async def delete(self, query: types.CallbackQuery or types.Message, callback_data: tools.Selector, state: aiogram.fsm.context.FSMContext,
                     api_repository: ApiRepository = Provide[Container.api_repository],
                     user: UserSession = None):

        if not (await api_repository.user_delete_async(callback_data.i, user.tokens.action_token)).is_success():
            raise Exception("error-invalid_operation")

        await self.wizard.goto((await self.wizard.manager.history.all())[-2].state)

    @scene.on.callback_query(tools.OptSelector.filter(aiogram.F.o == "back"))
    async def back(self, query: types.CallbackQuery or types.Message, callback_data: tools.OptSelector):
        await self.wizard.update_data({"selected_user": callback_data.i})
        await self.wizard.back()