import aiogram
from itertools import batched

from aiogram import filters, types
from aiogram.fsm import scene, context
from dependency_injector.wiring import inject, Provide

from src import ApiRepository
from src.core import UserSession
from src.infrastructure.services import Translator
from src.presentation import tools
from src.container import Container

from . import photos_and_name

category = "add_item"


class MainScene(scene.Scene, state="add_item"):

    @scene.on.message.enter()
    @scene.on.callback_query.enter()
    @tools.request_handler(auth=True, bypass_if_command=True, category=category, state="select_tag")
    @inject
    async def default_handler(self, query: types.CallbackQuery or types.Message,
                              translator: Translator = Provide[Container.translator],
                              api_repository: ApiRepository = Provide[Container.api_repository],
                              user: UserSession = None):

        text = translator.translate("add_item-text")
        tags = await api_repository.get_product_tags()

        all_data = await self.wizard.get_value("add_item", dict())
        if not all_data:
            all_data = dict()

        selected_tags: set = all_data.get("tags", set())
        parsed_tags = list(map(lambda x: types.InlineKeyboardButton(
            text=f"🔹  {translator.translate("pr-tag-" + x)}" if x not in selected_tags else f"✅  {translator.translate("pr-tag-" + x)}",
            callback_data=tools.Selector(i=x).pack()), tags))

        keyboard = [
            *batched(parsed_tags, 2),
            [
                types.InlineKeyboardButton(text="🟢 Далее", callback_data="next"),
                types.InlineKeyboardButton(text="🔴 Отмена", callback_data="cancel"),
            ],
        ]

        return {"text": text, "reply_markup": types.InlineKeyboardMarkup(inline_keyboard=keyboard)}

    @scene.on.callback_query(tools.Selector.filter())
    async def change_tags(self, query, callback_data: tools.Selector):
        all_data = await self.wizard.get_value("add_item", dict())
        if not all_data:
            all_data = dict()

        selected_tags: set = all_data.get("tags", set())
        if callback_data.i in selected_tags:
            selected_tags.remove(callback_data.i)
        else:
            selected_tags.add(callback_data.i)

        all_data["tags"] = selected_tags

        await self.wizard.update_data({"add_item": all_data})
        await self.wizard.retake()

    @scene.on.callback_query(aiogram.F.data == "cancel")
    async def cancel_operation(self, query):
        await self.wizard.update_data({"add_item": None})
        await self.wizard.exit()

    @scene.on.callback_query(aiogram.F.data == "next")
    async def next_operation(self, query):
        await self.wizard.goto(photos_and_name.PhotosAndName)