import aiogram

from aiogram import filters, types
from aiogram.fsm import scene, context
from dependency_injector.wiring import inject, Provide

from src.application.factories.key_link_factory import KeyLinkFactory
from src.core import UserSession, Key, KeyStatus
from src.infrastructure.services import Translator, ApiRepository
from src.infrastructure.services.rights_service import RightsService, Rights
from src.presentation import tools
from src.container import Container

from .rename import RenameScene
from .delete import DeleteScene
from .get_link import GetLinkScene
from .get_qr import GetQRScene
from .apps import AppsToConnect

category = "view_key"


class MainScene(scene.Scene, state="view_key"):

    @scene.on.message.enter()
    @scene.on.callback_query.enter()
    @tools.request_handler(auth=True, bypass_if_command=True, category=category)
    @inject
    async def default_handler(self, query: types.CallbackQuery or types.Message,
                              translator: Translator = Provide[Container.translator],
                              api_repository: ApiRepository = Provide[Container.api_repository],
                              user: UserSession = None):
        key_id = await self.wizard.get_value("selected_key")
        if not key_id:
            raise Exception("error-key-not-selected")

        key = await api_repository.get_key(key_id, user.tokens.action_token)
        if not key.is_success():
            raise Exception("error-key-not-found")
        key: Key = key.value

        text = translator.translate("view_key-text").format(
            key_id=key.id,
            key_name=key.name,
            key_location=translator.translate(f"location-{key.server.location}"),
            key_protocol=translator.translate(f"protocol-{key.protocol.name}"),
            key_port=key.server.port,
            all_traffic="N/A",
            download_traffic="N/A",
            upload_traffic="N/A",
            created_at=translator.date_to_text(key.created_at),
            key_is_active="✅" if key.status == KeyStatus.Enabled else "❌"
        )

        keyboard = [
            [
                types.InlineKeyboardButton(text=translator.translate("ui-tag-menu"), callback_data="menu"),

                types.InlineKeyboardButton(text=translator.translate("ui-tag-key-switch-off"),
                                           callback_data=tools.OptSelector(i=key.id, o="s-off").pack())
                if key.status == KeyStatus.Enabled else
                types.InlineKeyboardButton(text=translator.translate("ui-tag-key-switch-on"),
                                           callback_data=tools.OptSelector(i=key.id, o="s-on").pack()),

                types.InlineKeyboardButton(text=translator.translate("ui-tag-my_keys"), callback_data="keys")
            ],
            [
                types.InlineKeyboardButton(text=translator.translate("ui-tag-key-get_link"),
                                           callback_data=tools.OptSelector(i=key.id, o="lnk").pack()),
                types.InlineKeyboardButton(text=translator.translate("ui-tag-key-get_qr"),
                                           callback_data=tools.OptSelector(i=key.id, o="lqr").pack())
            ],
            [
                types.InlineKeyboardButton(text=translator.translate("ui-tag-key-rename"),
                                           callback_data=tools.OptSelector(i=key.id, o="ren").pack())
            ],
            [
                types.InlineKeyboardButton(text=translator.translate("ui-tag-key-apps"),
                                           callback_data=tools.OptSelector(i=key.id, o="app").pack())
            ],
            [
                types.InlineKeyboardButton(text=translator.translate("ui-tag-key-delete"),
                                           callback_data=tools.OptSelector(i=key.id, o="del").pack())
            ],
            [
                types.InlineKeyboardButton(text=translator.translate("ui-tag-key-how_to_use"), callback_data="menu")
            ]
        ]

        return {"text": text, "category_args": (translator.key_short_id(key.id),),
                "reply_markup": types.InlineKeyboardMarkup(inline_keyboard=keyboard)}

    @scene.on.callback_query(tools.OptSelector.filter(aiogram.F.o == "s-off"))
    @tools.request_handler(auth=True)
    @inject
    async def switch_off(self, query: types.CallbackQuery or types.Message, callback_data: tools.OptSelector,
                         api_repository: ApiRepository = Provide[Container.api_repository],
                         user: UserSession = None):
        result = await api_repository.key_turn_off(callback_data.i, user.tokens.action_token)
        if not result.is_success():
            raise Exception("error-key-action_aborted")

        await self.wizard.retake()

    @scene.on.callback_query(tools.OptSelector.filter(aiogram.F.o == "s-on"))
    @tools.request_handler(auth=True)
    @inject
    async def switch_on(self, query: types.CallbackQuery or types.Message, callback_data: tools.OptSelector,
                        api_repository: ApiRepository = Provide[Container.api_repository],
                        user: UserSession = None):
        result = await api_repository.key_turn_on(callback_data.i, user.tokens.action_token)
        if not result.is_success():
            raise Exception("error-key-action_aborted")

        await self.wizard.retake()

    @scene.on.callback_query(tools.OptSelector.filter(aiogram.F.o == "ren"))
    async def rename(self, query: types.CallbackQuery or types.Message, callback_data: tools.OptSelector,
                     user: UserSession = None):

        await self.wizard.update_data({"selected_key": callback_data.i})
        await self.wizard.goto(RenameScene)

    @scene.on.callback_query(tools.OptSelector.filter(aiogram.F.o == "del"))
    async def delete(self, query: types.CallbackQuery or types.Message, callback_data: tools.OptSelector,
                     user: UserSession = None):

        await self.wizard.update_data({"selected_key": callback_data.i})
        await self.wizard.goto(DeleteScene)

    @scene.on.callback_query(tools.OptSelector.filter(aiogram.F.o == "lnk"))
    async def get_link(self, query: types.CallbackQuery or types.Message, callback_data: tools.OptSelector,
                       user: UserSession = None):

        await self.wizard.update_data({"selected_key": callback_data.i})
        await self.wizard.goto(GetLinkScene)

    @scene.on.callback_query(tools.OptSelector.filter(aiogram.F.o == "lqr"))
    async def get_qr(self, query: types.CallbackQuery or types.Message, callback_data: tools.OptSelector,
                     user: UserSession = None):

        await self.wizard.update_data({"selected_key": callback_data.i})
        await self.wizard.goto(GetQRScene)

    @scene.on.callback_query(tools.OptSelector.filter(aiogram.F.o == "app"))
    async def apps_to_connect(self, query: types.CallbackQuery or types.Message, callback_data: tools.OptSelector,
                              user: UserSession = None):

        await self.wizard.update_data({"selected_key": callback_data.i})
        await self.wizard.goto(AppsToConnect)

    @scene.on.callback_query(tools.OptSelector.filter(aiogram.F.o == "back"))
    async def back(self, query: types.CallbackQuery or types.Message, callback_data: tools.OptSelector):
        await self.wizard.update_data({"selected_key": callback_data.i})
        await self.wizard.back()
