from aiogram import filters, types
from aiogram.fsm import scene, context
from dependency_injector.wiring import inject, Provide

from src.core import UserSession
from src.infrastructure.services import Translator
from src.infrastructure.services.rights_service import RightsService, Rights
from src.infrastructure.services.server_service import ServerService
from src.presentation import tools
from src.container import Container

category = "rates"


class MainScene(scene.Scene, state="rate"):

    @scene.on.message.enter()
    @scene.on.callback_query.enter()
    @tools.request_handler(auth=True, bypass_if_command=True, category=category)
    @inject
    async def default_handler(self, query: types.CallbackQuery or types.Message,
                              translator: Translator = Provide[Container.translator], user: UserSession = None):
        """
        text = (await langs.translate("rates-my_rate-text", language=language)).format(
            await langs.translate(f"rate-{user.Rate.Name}", language=language),
            user.Rate.Cost,
        )"""

        text = translator.translate("rates-my_rate-text").format(
            translator.translate("rates-rate_desc-text").format(
                name=translator.translate(f"rate-{user.data.rate.name}"),
                cost=user.data.rate.cost,
                keys_max=user.data.rate.maxKeys,
                devices_max=user.data.rate.maxConnections,
                download_speed=user.data.rate.trafficSpeedLimit,
                upload_speed=user.data.rate.trafficSpeedLimit
            )
        )

        if user.data.rate.isPrivate:
            text += translator.translate("rates-rate_desc-is_private")

        keyboard = [
            [
                types.InlineKeyboardButton(text=translator.translate("ui-tag-menu"),
                                           callback_data="menu")
            ],
            [
                types.InlineKeyboardButton(text=translator.translate("ui-tag-all_rates"),
                                           callback_data="rates")
            ]
        ]

        return {"text": text, "reply_markup": types.InlineKeyboardMarkup(inline_keyboard=keyboard)}
