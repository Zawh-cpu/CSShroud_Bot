import math

import aiogram

from aiogram import filters, types
from aiogram.fsm import scene, context
from dependency_injector.wiring import inject, Provide

from src.core import UserSession
from src.infrastructure.services import Translator, ApiRepository
from src.infrastructure.services.rights_service import RightsService, Rights
from src.infrastructure.services import ServerService
from src.presentation import tools
from src.container import Container
from src.application.dtos import KeysDto

category = "my_keys"


class MainScene(scene.Scene, state="my_keys"):

    @scene.on.message.enter()
    @scene.on.callback_query.enter()
    @tools.request_handler(auth=True, bypass_if_command=True, category=category)
    @inject
    async def default_handler(self, query: types.CallbackQuery or types.Message,
                              translator: Translator = Provide[Container.translator], server_service: ServerService = Provide[Container.server_service], api_repository: ApiRepository = Provide[Container.api_repository], user: UserSession = None):
        page = 0

        my_keys_dto: KeysDto = await api_repository.get_my_keys(user.tokens.action_token, page=0, size=10)
        max_pages = math.ceil(my_keys_dto.keys_count / 10)
        if not my_keys_dto:
            raise Exception("keys-parsing-failed")

        text = translator.translate("my_keys-text").format(
            keys_count=my_keys_dto.keys_count,
            max_keys=user.data.rate.maxKeys,
            active_keys=my_keys_dto.active_keys,

        )

        print(my_keys_dto.keys)

        keyboard = [
            [types.InlineKeyboardButton(text=translator.translate("ui-tag-menu"), callback_data="menu")],
            *[[types.InlineKeyboardButton(
                text=f"{"🟢" if key.IsActive else "🔴"}  #{key.Id} | {translator.translate(f"location-{key.LocationId}")} [{translator.translate(f"protocol-{key.ProtocolId}-short")}] | {key.Name}",
                callback_data="fwef")] for key in my_keys_dto.keys],
            [
                types.InlineKeyboardButton(text="◀️", callback_data="--page" if page > 0 else "None"),
                types.InlineKeyboardButton(text=f"{page + 1} / {max_pages}", callback_data="None"),
                types.InlineKeyboardButton(text="▶️", callback_data="++page" if page < max_pages - 1 else "None"),
            ]

        ]

        return {"text": text, "reply_markup": types.InlineKeyboardMarkup(inline_keyboard=keyboard)}
