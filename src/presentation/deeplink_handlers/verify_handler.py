import aiogram

from aiogram import filters, types
from dependency_injector.wiring import inject, Provide

from src.container import Container
from src.infrastructure.services import Translator, ApiRepository

from src.presentation import tools
from src.presentation.scenes import verify_auth
from aiogram.fsm import context, scene


async def verify_handler(message: types.Message, payload: object, state: context.FSMContext, scenes: scene.ScenesManager):
    verify_id = payload
    if verify_id is None:
        return

    await state.update_data({"verify_id": verify_id, "by_command": True})
    await scenes.enter(verify_auth.MainScene)
