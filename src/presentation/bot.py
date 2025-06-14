import aiogram

from aiogram import Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from dependency_injector.wiring import inject, Provide

from src.infrastructure.config import Config
from src.container import Container

from src.presentation.commands import router as command_router

dispatcher = Dispatcher()

from aiogram.fsm.scene import SceneRegistry
from src.presentation import scenes

from . import deep_link

scene_register = SceneRegistry(dispatcher)
scene_register.register(scenes.main.MainScene)
scene_register.register(scenes.profile.MainScene)
scene_register.register(scenes.my_rate.MainScene)
scene_register.register(scenes.all_rates.MainScene)
scene_register.register(scenes.my_keys.MainScene)
scene_register.register(scenes.add_key.SelectProtocol)
scene_register.register(scenes.admin_panel.MainScene, scenes.admin_panel.UsersList, scenes.admin_panel.ManageUserScene, scenes.admin_panel.DeleteScene, scenes.admin_panel.SetRoleScene, scenes.admin_panel.SetRateScene, scenes.admin_panel.SetRateTimeScene)
scene_register.register(scenes.key.MainScene, scenes.key.RenameScene, scenes.key.DeleteScene, scenes.key.GetLinkScene, scenes.key.GetQRScene, scenes.key.AppsToConnect)
scene_register.register(scenes.add_item.MainScene, scenes.add_item.PhotosAndName, scenes.add_item.ConfirmationScene)
scene_register.register(scenes.verify_auth.MainScene)

dispatcher.include_router(deep_link.start_router)
dispatcher.include_router(command_router)

from src.presentation.middlewares import album_middleware

dispatcher.message.middleware(album_middleware.AlbumMiddleware())

from . import plugin

@inject
async def start_telegram_bot(config: Config = Provide[Container.config]):
    tgbot = aiogram.Bot(token=config.BOT_TOKEN,
                    default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    plugin.bot = tgbot

    await dispatcher.start_polling(tgbot, skip_updates=True)