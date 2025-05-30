import aiogram

from aiogram import filters, types
from dependency_injector.wiring import inject, Provide

from src import Container
from src.infrastructure.services import Translator, ApiRepository
from src.application import dtos


@inject
async def verify_handler(message: types.Message, payload: dict, translator: Translator = Provide[Container.translator], api_repository: ApiRepository = Provide[Container.api_repository]):
    verify_id = payload.get("verify_id")
    if verify_id is None:
        await message.answer(translator.translate("invalid_start_command"))

    fl_data: dtos.Result[dtos.FastLoginInfoDto] = await api_repository.get_fastlogin_data_async(verify_id)