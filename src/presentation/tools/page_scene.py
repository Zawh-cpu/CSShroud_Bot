import aiogram

from aiogram import types
from aiogram.fsm import scene

from src.presentation.tools.selector import Selector


class PageScene(scene.Scene):
    _exit = None
    _next = None
    _data_label = None
    _page_name = "page"

    @scene.on.callback_query(aiogram.F.data == "exit")
    async def exit(self, query):
        await self.wizard.update_data({self.__class__._page_name: None})

        if not self.__class__._exit:
            await self.wizard.exit()
        else:
            await self.wizard.goto(self.__class__._exit)

    @scene.on.callback_query(aiogram.F.data == "back")
    async def back(self, query):
        await self.wizard.update_data({self.__class__._page_name: None})

        await self.wizard.back()

    @scene.on.callback_query(aiogram.F.data == "retake")
    async def retake(self, query):
        await self.wizard.retake()

    @scene.on.callback_query(aiogram.F.data == "back")
    async def back(self, query):
        await self.wizard.update_data({self.__class__._page_name: None})
        await self.wizard.back()

    @scene.on.callback_query(aiogram.F.data == "--page")
    async def page_previous(self, query):
        page = (await self.wizard.get_data()).get(self.__class__._page_name, 0) or 0
        await self.wizard.update_data({self.__class__._page_name: page - 1})
        await self.wizard.retake()

    @scene.on.callback_query(aiogram.F.data == "++page")
    async def page_next(self, query):
        page = (await self.wizard.get_data()).get(self.__class__._page_name, 0) or 0
        await self.wizard.update_data({self.__class__._page_name: page + 1})
        await self.wizard.retake()

    @scene.on.callback_query(aiogram.F.data == "None")
    async def pass_that(self, query):
        await query.answer()

    @scene.on.callback_query(Selector.filter())
    async def item_selected(self, callback_query: types.CallbackQuery, callback_data: Selector):
        await self.wizard.update_data({self.__class__._page_name: None, self.__class__._data_label: callback_data.i})
        await self.wizard.goto(self.__class__._next)
