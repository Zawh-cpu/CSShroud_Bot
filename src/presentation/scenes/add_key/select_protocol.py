import math

import aiogram

from aiogram import filters, types
from aiogram.fsm import scene
from dependency_injector.wiring import inject, Provide

from src import VpnProtocol
from src.core import UserSession, KeyStatus, protocol
from src.infrastructure.services import Translator, ApiRepository
from src.infrastructure.services.rights_service import RightsService, Rights
from src.infrastructure.services import ServerService
from src.presentation import tools
from src.container import Container
from src.application.dtos import AddKeyDto
from src.presentation.tools import PageScene, IntSelector

category = "add_key"


class SelectProtocol(PageScene, state="add_key"):

    @scene.on.message.enter()
    @scene.on.callback_query.enter()
    @tools.request_handler(auth=False, bypass_if_command=True, category=category)
    @inject
    async def default_handler(self, query: types.CallbackQuery or types.Message,
                              translator: Translator = Provide[Container.translator], server_service: ServerService = Provide[Container.server_service], user: UserSession = None):
        protocols = await server_service.get_protocols()

        text = "Select a protocol"

        keyboard = [
            *[
                [
                    types.InlineKeyboardButton(text=translator.translate(f"protocol-{protocol.name}"),
                                               callback_data=IntSelector(i=protocol).pack()) for protocol in protocols
                ]
            ]
        ]

        return {"text": text, "reply_markup": types.InlineKeyboardMarkup(inline_keyboard=keyboard)}

    @scene.on.callback_query(IntSelector.filter())
    @tools.request_handler(auth=True, category=category)
    @inject
    async def selected(self, query: types.CallbackQuery or types.Message, callback_data: IntSelector, api_repository: ApiRepository = Provide[Container.api_repository], user: UserSession = None):

        result = await api_repository.add_key(AddKeyDto(protocol=VpnProtocol(callback_data.i)), user.tokens.action_token)
        print(result)

        if result.is_success():
            await self.wizard.update_data({"selected_key": result.value})

        match result.status_code:
            case 403:
                raise Exception("error-keys-max_amount")
            case 503:
                raise Exception("error-daw-unavailable")

        raise Exception("error-internal-unknown")