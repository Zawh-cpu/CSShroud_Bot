import aiogram
import base64
import json

from aiogram import filters, types
from aiogram.fsm import context, scene

from src.presentation.scenes import *
from . import deeplink_handlers


def decode_deeplink(payload_str: str) -> list:
    """Декодирует base64-строку из Telegram deeplink в словарь"""
    try:
        decoded_bytes = base64.urlsafe_b64decode(payload_str)
        json_str = decoded_bytes.decode()
        return json_str.split("_", 1)
    except Exception:
        return {}


start_router = aiogram.Router()

@start_router.message(filters.CommandStart(deep_link=True))
async def start_handler(message: types.Message, command: filters.CommandStart, state: context.FSMContext, scenes: scene.ScenesManager):
    print("aaaaa")
    param = command.args
    if not param:
        await message.answer("Привет! Бот запущен без параметров.")
        return

    payload = decode_deeplink(param)
    if len(payload) < 2:
        return

    match payload[0]:
        case "verify":
            await deeplink_handlers.verify_handler(message, payload[1], state, scenes)

        case _:
            await state.update_data({"by_command": True})
            await scenes.enter(main.MainScene)
