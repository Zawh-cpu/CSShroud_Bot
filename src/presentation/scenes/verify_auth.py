import aiogram

from aiogram import filters, types
from aiogram.fsm import scene, context
from dependency_injector.wiring import inject, Provide

from src.core import UserSession
from src.infrastructure.services import Translator, ApiRepository, Translator, translator
from src.infrastructure.services.rights_service import RightsService, Rights
from src.presentation import tools
from src.container import Container

from src.application import dtos

category = "verify_auth"


class MainScene(scene.Scene, state="verify_auth"):

    @scene.on.message.enter()
    @scene.on.callback_query.enter()
    @tools.request_handler(auth=False, bypass_if_command=True, category=category)
    @inject
    async def default_handler(self, query: types.CallbackQuery or types.Message,
                              translator: Translator = Provide[Container.translator],
                              api_repository: ApiRepository = Provide[Container.api_repository],
                              user: UserSession = None):
        verify_id = await self.wizard.get_value("verify_id")
        if verify_id is None:
            raise Exception("error-verify")

        fl_data: dtos.Result[dtos.FastLoginInfoDto] = await api_repository.get_fastlogin_data_async(verify_id)
        if not fl_data.is_success():
            raise Exception("error-verify")

        text = translator.translate("verify_handler-text")
        keyboard = [
            [
                types.InlineKeyboardButton(text=translator.translate("ui-tag-cancel"),
                                           callback_data=tools.DuoSelector(i=fl_data.value.id, j="cancel").pack())
            ],
            [
                types.InlineKeyboardButton(text=str(i),
                                           callback_data=tools.DuoSelector(i=fl_data.value.id, j=str(i)).pack()) for i
                in fl_data.value.variants
            ]
        ]

        return {"text": text, "reply_markup": types.InlineKeyboardMarkup(inline_keyboard=keyboard)}

    @scene.on.callback_query(tools.DuoSelector.filter(aiogram.F.j == "cancel"))
    @tools.request_handler(auth=True)
    @inject
    async def cancel(self, query: types.CallbackQuery, callback_data: tools.DuoSelector, api_repository: ApiRepository = Provide[Container.api_repository], user: UserSession = None):
        await api_repository.fastlogin_try_claim_async(callback_data.i, -1000, user.tokens.action_token)
        await self.wizard.exit()


    @scene.on.callback_query(tools.DuoSelector.filter())
    @tools.request_handler(auth=True, category=category)
    @inject
    async def select_number(self, query: types.CallbackQuery or types.Message, callback_data: tools.DuoSelector,
                            api_repository: ApiRepository = Provide[Container.api_repository], translator: Translator = Provide[Container.translator],
                            user: UserSession = None):

        result = await api_repository.fastlogin_try_claim_async(callback_data.i, int(callback_data.j),
                                                                user.tokens.action_token)
        if result.is_success():
            text = translator.translate("verify_handler-successfully-text")
        else:
            text = translator.translate("verify_handler-failed-text")

        keyboard = [
            [types.InlineKeyboardButton(text=translator.translate("ui-tag-menu"),
                                        callback_data="menu")],
            [types.InlineKeyboardButton(text=translator.translate("ui-tag-ok"),
                                        callback_data="continue")]
        ]

        return {"text": text, "reply_markup": types.InlineKeyboardMarkup(inline_keyboard=keyboard)}

    @scene.on.callback_query(aiogram.F.data == "continue")
    async def continue_this(self, query: types.CallbackQuery):
        await query.message.delete()