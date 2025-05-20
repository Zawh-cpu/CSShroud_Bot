import aiogram

from aiogram import types
from aiogram.fsm import scene
from dependency_injector.wiring import inject, Provide

from src.application.factories import KeyLinkFactory
from src.core import UserSession
from src.infrastructure.services import Translator, ApiRepository
from src.presentation import tools
from src.container import Container

category = "view_key"


class GetLinkScene(scene.Scene, state="view_key-get_link"):

    @scene.on.message.enter()
    @scene.on.callback_query.enter()
    @tools.request_handler(auth=True, category=category, state="get_link")
    @inject
    async def default_handler(self, query: types.CallbackQuery or types.Message,
                              translator: Translator = Provide[Container.translator],
                              api_repository: ApiRepository = Provide[Container.api_repository],
                              user: UserSession = None):

        key_id = await self.wizard.get_value("selected_key")
        if not key_id:
            raise Exception("error-key-not-selected")

        data = await api_repository.key_get_connect_data(key_id, user.tokens.action_token)
        if not data:
            raise Exception("error-key-action_aborted")

        link = KeyLinkFactory.get_link(data.value, translator.translate("key-name-short").format(
            protocol=translator.translate(f"protocol-{data.value.protocol.name}-short"),
            short_id=translator.key_short_id(data.value.id)
        ))

        text = translator.translate("view_key-get_link-text").format(link=link)
        keyboard = [
            [
                types.InlineKeyboardButton(text=translator.translate("ui-tag-menu"), callback_data="menu"),

                types.InlineKeyboardButton(text=translator.translate("ui-tag-back"),
                                           callback_data=tools.OptSelector(i=key_id, o="back").pack()),

                types.InlineKeyboardButton(text=translator.translate("ui-tag-my_keys"), callback_data="keys")
            ]
        ]

        return {"text": text, "category_args": (translator.key_short_id(key_id),),
                "reply_markup": types.InlineKeyboardMarkup(inline_keyboard=keyboard)}

    @scene.on.callback_query(tools.OptSelector.filter(aiogram.F.o == "back"))
    async def back(self, query: types.CallbackQuery or types.Message, callback_data: tools.OptSelector):
        await self.wizard.update_data({"selected_key": callback_data.i})
        await self.wizard.back()