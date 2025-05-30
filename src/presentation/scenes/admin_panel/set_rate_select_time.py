import datetime

import aiogram

from aiogram import filters, types
from aiogram.fsm import scene, context
from dependency_injector.wiring import inject, Provide

from src import PatchUserDto
from src.application.dtos import PatchKeyDto
from src.core import UserSession, Key, KeyStatus
from src.infrastructure.services import Translator, ApiRepository, ServerService
from src.infrastructure.services.rights_service import RightsService, Rights
from src.presentation import tools
from src.container import Container

category = "admin_panel"


class SetRateTimeScene(scene.Scene, state="admin_panel-set_rate-time"):

    @scene.on.message.enter()
    @scene.on.callback_query.enter()
    @tools.request_handler(auth=True, category=category, state="set_rate-time")
    @inject
    async def default_handler(self, query: types.CallbackQuery or types.Message,
                              translator: Translator = Provide[Container.translator],
                              api_repository: ApiRepository = Provide[Container.api_repository],
                              user: UserSession = None):
        selected_user_id = (await self.wizard.get_data()).get("selected_user")
        selected_rate = (await self.wizard.get_data()).get("selected_rate")
        if not (selected_user_id and selected_rate):
            raise Exception("error-invalid_arguments")

        selected_user = await api_repository.get_user_by_id_info_async(selected_user_id, user.tokens.action_token)
        if not selected_user.is_success():
            raise Exception(f"error-invalid_user")

        print(selected_user)
        print(selected_user.value)

        text = translator.translate("admin_panel-manage_user-set_rate_time-text").format(translator.translate(f"rate-{selected_user.value.rate.name}"),
                                                                                         translator.date_to_text(selected_user.value.payed_until))

        time_table = [0, 30, 60, 90, 180, 270, 360]

        now = (selected_user.value.payed_until.replace(microsecond=0) or datetime.datetime.now(datetime.timezone.utc)).replace(microsecond=0).timestamp()

        keyboard = [
            [
                types.InlineKeyboardButton(text=translator.translate("ui-tag-menu"), callback_data="menu"),
                types.InlineKeyboardButton(text=translator.translate("ui-tag-back-short"),
                                           callback_data=tools.OptSelector(i=selected_user_id, o="back").pack()),
                types.InlineKeyboardButton(text=translator.translate("ui-tag-cancel-short"),
                                           callback_data=tools.OptSelector(i=selected_user_id, o="cancel").pack()),
                types.InlineKeyboardButton(text=translator.translate("ui-tag-my_keys"), callback_data="keys")
            ],
            *[[types.InlineKeyboardButton(text=translator.translate(f"+{time // 30}мес."), callback_data=tools.DuoSelector(i=selected_user_id, j=str(int(now + (time * 86400)))).pack())] for time in time_table]
        ]

        return {"text": text, "category_args": (translator.key_short_id(selected_user_id),), "reply_markup": types.InlineKeyboardMarkup(inline_keyboard=keyboard)}

    @scene.on.callback_query(tools.DuoSelector.filter())
    @tools.request_handler(auth=True)
    @inject
    async def select_time(self, query: types.CallbackQuery or types.Message, callback_data: tools.DuoSelector,
                     api_repository: ApiRepository = Provide[Container.api_repository],
                     user: UserSession = None):

        selected_rate = (await self.wizard.get_data()).get("selected_rate")
        if not selected_rate:
            raise Exception("error-invalid_arguments")

        if not (await api_repository.user_patch_async(callback_data.i, PatchUserDto(
            rate_id=selected_rate,
            rate_payed_until=datetime.datetime.fromtimestamp(float(callback_data.j), tz=datetime.timezone.utc).isoformat().replace("+00:00", "Z"),
        ), user.tokens.action_token)).is_success():
            raise Exception("error-invalid_operation")

        await self.wizard.goto((await self.wizard.manager.history.all())[-2].state)


    @scene.on.message()
    @tools.request_handler(auth=True)
    @inject
    async def select_time_chat(self, query: types.Message,
                     api_repository: ApiRepository = Provide[Container.api_repository],
                     user: UserSession = None):

        selected_rate = (await self.wizard.get_data()).get("selected_rate")
        selected_user = (await self.wizard.get_data()).get("selected_user")
        if not (selected_rate and selected_user):
            raise Exception("error-invalid_arguments")

        data = query.text.split(".")
        if len(data) != 3:
            raise Exception("error-invalid_arguments")

        date = datetime.datetime(year=int(data[0]), month=int(data[1]), day=int(data[2]), tzinfo=datetime.timezone.utc)

        if not (await api_repository.user_patch_async(selected_user, PatchUserDto(
            rate_id=selected_rate,
            rate_payed_until=date.isoformat().replace("+00:00", "Z"),
        ), user.tokens.action_token)).is_success():
            raise Exception("error-invalid_operation")

        await self.wizard.goto((await self.wizard.manager.history.all())[-2].state)

    @scene.on.callback_query(tools.OptSelector.filter(aiogram.F.o == "back"))
    async def back(self, query: types.CallbackQuery or types.Message, callback_data: tools.OptSelector):
        await self.wizard.update_data({"selected_user": callback_data.i, "selected_rate": None})
        await self.wizard.back()

    @scene.on.callback_query(tools.OptSelector.filter(aiogram.F.o == "cancel"))
    async def cancel(self, query: types.CallbackQuery or types.Message, callback_data: tools.OptSelector):
        await self.wizard.update_data({"selected_user": callback_data.i, "selected_rate": None})
        await self.wizard.goto((await self.wizard.manager.history.all())[-2].state)