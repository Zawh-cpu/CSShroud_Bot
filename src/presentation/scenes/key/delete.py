import aiogram

from aiogram import filters, types
from aiogram.fsm import scene, context
from dependency_injector.wiring import inject, Provide

from src.application.dtos import PatchKeyDto
from src.core import UserSession, Key, KeyStatus
from src.infrastructure.services import Translator, ApiRepository
from src.infrastructure.services.rights_service import RightsService, Rights
from src.presentation import tools
from src.container import Container

category = "view_key"


class DeleteScene(scene.Scene, state="view_key-delete"):

    @scene.on.message.enter()
    @scene.on.callback_query.enter()
    @tools.request_handler(auth=False, category=category, state="delete")
    @inject
    async def default_handler(self, query: types.CallbackQuery or types.Message,
                              translator: Translator = Provide[Container.translator],
                              api_repository: ApiRepository = Provide[Container.api_repository],
                              user: UserSession = None):

        key_id = await self.wizard.get_value("selected_key")
        if not key_id:
            raise Exception("error-key-not-selected")

        text = translator.translate("view_key-delete-text")

        keyboard = [
            [
                types.InlineKeyboardButton(text=translator.translate("ui-tag-menu"), callback_data="menu"),
                types.InlineKeyboardButton(text=translator.translate("ui-tag-my_keys"), callback_data="keys")
            ],
            [
                types.InlineKeyboardButton(text=translator.translate("ui-tag-confirm-short"), callback_data=tools.Selector(i=key_id).pack()),
                types.InlineKeyboardButton(text=translator.translate("ui-tag-cancel-short"),
                                           callback_data=tools.OptSelector(i=key_id, o="back").pack())
            ]
        ]

        return {"text": text, "category_args": (translator.key_short_id(key_id),), "reply_markup": types.InlineKeyboardMarkup(inline_keyboard=keyboard)}

    @scene.on.callback_query(tools.Selector.filter())
    @tools.request_handler(auth=True)
    @inject
    async def delete(self, query: types.CallbackQuery or types.Message, callback_data: tools.Selector, state: aiogram.fsm.context.FSMContext,
                     api_repository: ApiRepository = Provide[Container.api_repository],
                     user: UserSession = None):

        await api_repository.key_delete(callback_data.i, user.tokens.action_token)
        await self.wizard.goto((await self.wizard.manager.history.all())[-2].state)

    @scene.on.callback_query(tools.OptSelector.filter(aiogram.F.o == "back"))
    async def back(self, query: types.CallbackQuery or types.Message, callback_data: tools.OptSelector):
        await self.wizard.update_data({"selected_key": callback_data.i})
        await self.wizard.back()