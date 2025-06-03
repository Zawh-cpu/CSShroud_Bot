import aiogram

from aiogram import filters, types
from aiogram.fsm import context, scene

from src.presentation.scenes import *

router = aiogram.Router()


# @router.message(filters.CommandStart())
@router.callback_query(aiogram.F.data == "menu")
async def command_start(message: types.Message, state: context.FSMContext, scenes: scene.ScenesManager):
    await state.update_data({"by_command": True})
    await scenes.enter(main.MainScene)


@router.message(filters.Command("add_item"))
@router.callback_query(aiogram.F.data == "add_item")
async def command_add_item(message: types.Message, state: context.FSMContext, scenes: scene.ScenesManager):
    await state.update_data({"by_command": True})
    await scenes.enter(add_item.MainScene)

@router.message(filters.Command("profile"))
@router.callback_query(aiogram.F.data == "profile")
async def command_profile(message: types.Message, state: context.FSMContext, scenes: scene.ScenesManager):
    await state.update_data({"by_command": True})
    await scenes.enter(profile.MainScene)


@router.message(filters.Command("rate"))
@router.callback_query(aiogram.F.data == "rate")
async def command_my_rate(message: types.Message, state: context.FSMContext, scenes: scene.ScenesManager):
    await state.update_data({"by_command": True})
    await scenes.enter(my_rate.MainScene)


@router.message(filters.Command("rates"))
@router.callback_query(aiogram.F.data == "rates")
async def command_rates(message: types.Message, state: context.FSMContext, scenes: scene.ScenesManager):
    await state.update_data({"by_command": True})
    await scenes.enter(all_rates.MainScene)


@router.message(filters.Command("keys"))
@router.callback_query(aiogram.F.data == "keys")
async def command_keys(message: types.Message, state: context.FSMContext, scenes: scene.ScenesManager):
    await state.update_data({"by_command": True})
    await scenes.enter(my_keys.MainScene)


@router.message(filters.Command("add_key"))
@router.callback_query(aiogram.F.data == "add_key")
async def command_add_key(message: types.Message, state: context.FSMContext, scenes: scene.ScenesManager):
    await state.update_data({"by_command": True})
    await scenes.enter(add_key.SelectProtocol)


@router.message(filters.Command("admin"))
@router.callback_query(aiogram.F.data == "admin")
async def command_admin(message: types.Message, state: context.FSMContext, scenes: scene.ScenesManager):
    await state.update_data({"by_command": True})
    await scenes.enter(admin_panel.MainScene)
