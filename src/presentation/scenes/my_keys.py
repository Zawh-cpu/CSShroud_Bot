import math

import aiogram

from aiogram import filters, types
from aiogram.fsm import scene
from dependency_injector.wiring import inject, Provide

from src.core import UserSession, KeyStatus
from src.infrastructure.services import Translator, ApiRepository
from src.infrastructure.services.rights_service import RightsService, Rights
from src.infrastructure.services import ServerService
from src.presentation import tools
from src.container import Container
from src.application.dtos import KeysDto
from src.presentation.tools.page_scene import PageScene

category = "my_keys"


class MainScene(PageScene, state="my_keys"):

    @scene.on.message.enter()
    @scene.on.callback_query.enter()
    @tools.request_handler(auth=True, bypass_if_command=True, category=category)
    @inject
    async def default_handler(self, query: types.CallbackQuery or types.Message,
                              translator: Translator = Provide[Container.translator], server_service: ServerService = Provide[Container.server_service], api_repository: ApiRepository = Provide[Container.api_repository], user: UserSession = None):
        page = await self.wizard.get_value("page", 0)

        my_keys_dto: KeysDto = await api_repository.get_my_keys(user.tokens.action_token, page=page, size=10)
        max_pages = math.ceil(my_keys_dto.keys_count / 10)
        if not my_keys_dto:
            raise Exception("keys-parsing-failed")

        text = translator.translate("my_keys-text").format(
            keys_count=my_keys_dto.keys_count,
            max_keys=user.data.rate.maxKeys,
            active_keys=my_keys_dto.active_keys,

        )

        keyboard = [
            [types.InlineKeyboardButton(text=translator.translate("ui-tag-menu"), callback_data="menu"),
             types.InlineKeyboardButton(
                 text=(translator.translate("ui-tag-create_key-ok")).format(my_keys_dto.keys_count, user.data.rate.maxKeys),
                 callback_data="add_key")
             if my_keys_dto.keys_count < user.data.rate.maxKeys else
             types.InlineKeyboardButton(
                 text=(translator.translate("ui-tag-create_key-forbidden")).format(my_keys_dto.keys_count, user.data.rate.maxKeys),
                 callback_data="None"),
             ],
            *[[types.InlineKeyboardButton(
                text=f"{"🟢" if key.status == KeyStatus.Enabled else "🔴"}  #{key.id[4:8] + key.id[9:13]} | {translator.translate(f"location-{key.server.location}")} [{translator.translate(f"protocol-{key.protocol.name}-short")}] | {key.name}",
                callback_data="fwef")] for key in my_keys_dto.keys],
            [
                types.InlineKeyboardButton(text="◀️", callback_data="--page" if page > 0 else "None"),
                types.InlineKeyboardButton(text=f"{page + 1} / {max_pages}", callback_data="None"),
                types.InlineKeyboardButton(text="▶️", callback_data="++page" if page < max_pages - 1 else "None"),
            ]

        ]

        return {"text": text, "reply_markup": types.InlineKeyboardMarkup(inline_keyboard=keyboard)}
