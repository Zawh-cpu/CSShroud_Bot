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

scene_register = SceneRegistry(dispatcher)
scene_register.register(scenes.main.MainScene)
scene_register.register(scenes.profile.MainScene)
scene_register.register(scenes.my_rate.MainScene)
scene_register.register(scenes.all_rates.MainScene)
scene_register.register(scenes.my_keys.MainScene)
scene_register.register(scenes.add_item.MainScene, scenes.add_item.PhotosAndName, scenes.add_item.ConfirmationScene)

dispatcher.include_router(command_router)

from src.presentation.middlewares import album_middleware

dispatcher.message.middleware(album_middleware.AlbumMiddleware())


@inject
async def start_telegram_bot(config: Config = Provide[Container.config]):
    print("afrwaefqf")
    tgbot = aiogram.Bot(token=config.BOT_TOKEN,
                    default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    await dispatcher.start_polling(tgbot, skip_updates=True)
