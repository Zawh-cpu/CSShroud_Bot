import aiogram
from aiogram.fsm import scene


class Scene(scene.Scene):
    _exit = None

    @scene.on.callback_query(aiogram.F.data == "exit")
    async def exit(self, query):

        if not self.__class__._exit:
            await self.wizard.exit()
        else:
            await self.wizard.goto(self.__class__._exit)

    @scene.on.callback_query(aiogram.F.data == "back")
    async def back(self, query):
        await self.wizard.back()

    @scene.on.callback_query(aiogram.F.data == "retake")
    async def retake(self, query):
        await self.wizard.retake()
