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

category = "add_item"


class ConfirmationScene(tools.Scene, state="add_item-confirmation"):

    @scene.on.message.enter()
    @scene.on.callback_query.enter()
    @tools.request_handler(auth=True, category=category, state="confirmation")
    @inject
    async def default_handler(self, query: types.CallbackQuery or types.Message,
                              translator: Translator = Provide[Container.translator],
                              redis_repository: RedisRepository = Provide[Container.redis_repository],
                              user: UserSession = None):

        add_item = await self.wizard.get_value("add_item") or dict()
        add_item["state"] = None,
        await self.wizard.update_data({"add_item": add_item})

        tags = add_item.get("tags", None)
        if not tags:
            tags = ["Other"]
        media_group = add_item.get("media")
        description = add_item.get("desc")

        item_options = description.get("tags")

        if not (media_group):
            raise Exception("product-session-expired")

        if item_options:
            print(item_options)
            body_query = translator.translate("product-label-options").format(
                    "".join(map(lambda x: f"\n  - <b>{translator.translate(f"product-options-{x}")}</b>: {item_options[x]}", item_options)),
                    translator.translate("product-label-body").format(
                            "г. Пенза, ул. Проспект Победы 14",
                            description.get("cost"),
                            "UF24-AJK4-HIK3-ALB4",
                            "\n  - @ZawhZ\n  - @ZawhZ\n  - @ZawhZ",
                            " ".join(map(lambda x: f"#{translator.translate(f"pr-tag-{x}-post")}", tags))
                    )
            )
        else:
            body_query = translator.translate("product-label-body").format(
                "г. Пенза, ул. Проспект Победы 14",
                description.get("cost"),
                "FFFF-FFFF-FFFF-FFFF",
                "\n  - @ZawhZ\n  - @ZawhZ\n  - @ZawhZ",
                " ".join(map(lambda x: f"#{translator.translate(f"pr-tag-{x}-post")}", tags))
            )


        text = translator.translate("add_item-confirmation").format(
            translator.translate("product-label-header").format(
                description.get("title"), description.get("desc"),
                body_query
            )
        )

        keyboard = [

            [
                types.InlineKeyboardButton(text="🔄 Регенерировать", callback_data="regenerate"),
            ],
            [
                types.InlineKeyboardButton(text="💰 Изменить цену", callback_data="change_cost"),
                types.InlineKeyboardButton(text="🖼️ Изменить медиа", callback_data="change_media")
            ],
            [
                types.InlineKeyboardButton(text="📝 Изменить описание", callback_data="change_desc")
            ],
            [
                types.InlineKeyboardButton(text="🪄 Переделать промпт с помощью AI", callback_data="change_prompt"),
            ],
            [
                types.InlineKeyboardButton(text="📤 Отправить", callback_data="upload"),
                types.InlineKeyboardButton(text="🔴 Отмена", callback_data="cancel"),
                types.InlineKeyboardButton(text="📤❌ Без описания", callback_data="upload_mini"),
            ]
        ]

        media_response = list()
        for media in media_group:
            _type = media.get("type")
            if _type == "photo":
                media_response.append(types.InputMediaPhoto(media=media["id"]))
            elif _type.startswith("video"):
                media_response.append(types.InputMediaVideo(media=media["id"]))


        return {"text": text, "media": media_response, "reply_markup": types.InlineKeyboardMarkup(inline_keyboard=keyboard)}

    @scene.on.callback_query(aiogram.F.data == "regenerate")
    @tools.request_handler(auth=True)
    @inject
    async def regenerate(self, query: types.CallbackQuery or types.Message,
                              ai_repository: AiRepository = Provide[Container.ai_repository],
                              user: UserSession = None):
        add_item = await self.wizard.get_value("add_item")
        if not add_item:
            raise Exception("product-session-expired")

        prompt = add_item.get("prompt")
        if not prompt:
            await query.answer("Ваш промпт не был сохранён")
            return

        data = await ai_repository.parse_response(prompt)
        add_item["desc"] = data

        await self.wizard.update_data({"add_item": add_item})
        await self.wizard.retake()

    @scene.on.callback_query(aiogram.F.data == "change_desc")
    @inject
    async def regenerate(self, query: types.CallbackQuery or types.Message,
                         translator: Translator = Provide[Container.translator],
                         user: UserSession = None):
        add_item = await self.wizard.get_value("add_item")
        if not add_item:
            raise Exception("product-session-expired")
        add_item["state"] = "change_desc"

        desc = add_item.get("desc")
        if not desc:
            desc = "К сожалению, ваше описание не сохранилось"

        await self.wizard.update_data({"add_item": add_item})

    #@scene.on.message():

