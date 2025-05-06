import aiogram

from aiogram import filters, types
from aiogram.fsm import context, scene

from src.presentation.scenes import *

router = aiogram.Router()


@router.message(filters.CommandStart())
@router.callback_query(aiogram.F.data == "menu")
async def command_start(message: types.Message, state: context.FSMContext, scenes: scene.ScenesManager):
    await state.update_data({"by_command": True})
    await scenes.enter(main.MainScene)


@router.message(filters.Command("add_item"))
@router.callback_query(aiogram.F.data == "add_item")
async def command_start(message: types.Message, state: context.FSMContext, scenes: scene.ScenesManager):
    await state.update_data({"by_command": True})
    await scenes.enter(add_item.MainScene)
