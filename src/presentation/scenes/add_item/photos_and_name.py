import aiogram
from itertools import batched

from aiogram import filters, types
from aiogram.fsm import scene, context
from dependency_injector.wiring import inject, Provide

from src import ApiRepository, RedisRepository, AiRepository
from src.core import UserSession
from src.infrastructure.services import Translator
from src.presentation import tools
from src.container import Container
from .confirmation import ConfirmationScene

category = "add_item"


class PhotosAndName(scene.Scene, state="add_item-phAndName"):

    @scene.on.message.enter()
    @scene.on.callback_query.enter()
    @tools.request_handler(auth=True, category=category, state="photos_and_name")
    @inject
    async def default_handler(self, query: types.CallbackQuery or types.Message,
                              translator: Translator = Provide[Container.translator],
                              api_repository: ApiRepository = Provide[Container.api_repository],
                              user: UserSession = None):

        text = translator.translate("add_item-photos_and_name")

        keyboard = [
            [
                types.InlineKeyboardButton(text="🔙 Назад", callback_data="back"),
            ],
            [
                types.InlineKeyboardButton(text="🟢 Далее", callback_data="None"),
                types.InlineKeyboardButton(text="🔴 Отмена", callback_data="cancel"),
            ],
        ]

        return {"text": text, "reply_markup": types.InlineKeyboardMarkup(inline_keyboard=keyboard)}

    @scene.on.callback_query(aiogram.F.data == "back")
    async def back(self, query: types.Message or types.CallbackQuery):
        await self.wizard.back()

    @scene.on.message(aiogram.F.content_type.in_([types.ContentType.PHOTO, types.ContentType.VIDEO]))
    # @scene.on.message(aiogram.F.content_type.in_([types.ContentType.PHOTO]))
    @inject
    async def action(self, query: types.Message, album: list[types.Message], redis_repository: RedisRepository = Provide[Container.redis_repository], ai_repository: AiRepository = Provide[Container.ai_repository]):
        documents = [(sheet.video or (sheet.photo or [])[-1]) for sheet in album]
        parsed_docs = list()
        print("DOCS", documents)
        for doc in documents:
            parsed_docs.append({"id": doc.file_id, "type": doc.mime_type if type(doc) is not types.PhotoSize else "photo"})
        add_item = await self.wizard.get_value("add_item") or dict()
        add_item["media"] = parsed_docs
        # add_item["media"] = documents

        if query.caption:
            data = await ai_repository.parse_response(query.caption)
            add_item["prompt"] = query.caption
            add_item["desc"] = data

        await self.wizard.update_data({"add_item": add_item})
        await self.wizard.goto(ConfirmationScene)

    @scene.on.callback_query(aiogram.F.data == "cancel")
    async def cancel_operation(self, query):
        await self.wizard.update_data({"add_item": None})
        await self.wizard.exit()
