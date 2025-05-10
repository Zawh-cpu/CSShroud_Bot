from aiogram import filters, types
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm import scene, context
from dependency_injector.wiring import inject, Provide

from src.presentation.tools.selector import IntSelector
from src.core import UserSession
from src.infrastructure.services import Translator
from src.infrastructure.services.rights_service import RightsService, Rights
from src.infrastructure.services.server_service import ServerService
from src.presentation import tools
from src.container import Container

category = "rates"


class MainScene(scene.Scene, state="rates"):

    @scene.on.message.enter()
    @scene.on.callback_query.enter()
    @tools.request_handler(auth=True, bypass_if_command=True, category=category)
    @inject
    async def default_handler(self, query: types.CallbackQuery or types.Message,
                              translator: Translator = Provide[Container.translator], server_service: ServerService = Provide[Container.server_service], user: UserSession = None):
        cshn_rate_num = await self.wizard.get_value("chosen_rate", 0)

        rates = list(sorted(await server_service.get_rates(), key=lambda rate: rate.cost))
        chosen_rate = list(filter(lambda x: x.id == cshn_rate_num, rates))
        if chosen_rate:
            chosen_rate = chosen_rate[0]
        else:
            chosen_rate = rates[0]

        text = translator.translate("rates-all_rates-text").format(
            translator.translate("rates-rate_desc-compare-text").format(
                name=translator.translate(f"rate-{chosen_rate.name}"),
                cost=chosen_rate.cost,
                keys_max=chosen_rate.maxKeys,
                devices_max=chosen_rate.maxConnections,
                download_speed=chosen_rate.trafficSpeedLimit,
                upload_speed=chosen_rate.trafficSpeedLimit,
                compare_cost=user.data.rate.cost,
                compare_keys_max=user.data.rate.maxKeys,
                compare_devices_max=user.data.rate.maxConnections,
                compare_download_speed=user.data.rate.trafficSpeedLimit,
                compare_upload_speed=user.data.rate.trafficSpeedLimit
            )
        )

        keyboard = [
            [
                types.InlineKeyboardButton(text=translator.translate("ui-tag-menu"),
                                           callback_data="menu"),
                types.InlineKeyboardButton(text=translator.translate("ui-tag-my_rate"),
                                           callback_data="rate")
            ],
            *[[
                types.InlineKeyboardButton(text=f"{translator.translate(f"rate-{rate.name}")}  ({rate.cost}₽/мес.)",
                                           callback_data=IntSelector(i=rate.id).pack())
                if rate != chosen_rate
                else
                types.InlineKeyboardButton(text=f"▶️ {translator.translate(f"rate-{rate.name}")}  ({rate.cost}₽/мес.) ◀️",
                                           callback_data="None")
            ] for rate in rates]
        ]

        return {"text": text, "reply_markup": types.InlineKeyboardMarkup(inline_keyboard=keyboard)}

    @scene.on.callback_query(IntSelector.filter())
    async def select_rate(self, query: types.CallbackQuery or types.Message, callback_data: IntSelector):
        await self.wizard.update_data({"chosen_rate": callback_data.i})
        await self.wizard.retake()