import functools
import datetime as dt
import time

from aiogram import types
from aiogram.fsm import scene
from pycparser.ply.yacc import resultlimit

from src import UserRepository

from dependency_injector.wiring import inject, Provide
from src.container import Container
from src.infrastructure.services import Translator


def request_handler(auth=True, category=None, category_args=None, state=None, callback_index=1, bypass_if_command=False):
    def decorator(func):
        @functools.wraps(func)
        @inject
        async def wrapper(*args, user_repository: UserRepository = Provide[Container.user_repository], translator: Translator = Provide[Container.translator], **kwargs):
            wizard: scene.SceneWizard = args[0].wizard
            wizard_data = await wizard.get_data()
            if bypass_if_command:

                if wizard_data.get("by_command"):
                    await wizard.update_data({"by_command": False})
                    return

            query = args[callback_index]

            try:
                if auth:
                    session = await user_repository.get_session_by_telegram_id_async(query.from_user.id)
                    # print("HANDLER && SESSION -> GOT IT!", session)
                    if not session:
                        # print("HANDLER -- SESSION -> RESET!")
                        session = await user_repository.signup_user_async(query.from_user.id, query.from_user.first_name, query.from_user.last_name)
                        # There's really needs to make an error for server invalid error
                        if not session:
                            print("ERROR -- NOT SESSION SPECIFIED")
                else:
                    session = None

                kwargs["user"] = session

                result = await func(*args, **kwargs)
                if result:
                    if state:
                        header_text = f"<b>{translator.translate(category)}   <i>///   {translator.translate(f"{category}-{state}")}</i></b>"
                    else:
                        header_text = f"<b>{translator.translate(category)}</b>"

                    result_args = result.get("category_args")
                    if result_args:
                        result["text"] = f"{header_text.format(*result_args)}\n\n{result.get("text", "")}"
                    else:
                        result["text"] = f"{header_text}\n\n{result.get("text", "")}"

                    media = result.get("media")
                    if media:
                        await query.message.delete()
                        await query.message.answer_photo(photo=media[0], caption=result.get("text", ""), reply_markup=result.get("reply_markup", None))
                        return

                    if isinstance(query, types.CallbackQuery):
                        if query.message.text and (dt.datetime.now(dt.UTC) - query.message.date).days < 1:
                            await query.message.edit_text(**result)
                        else:
                            await query.message.delete()
                            await query.message.answer(**result)
                    else:
                        if media := result.get("media"):
                            await query.answer_media_group(media)
                            del result["media"]
                        await query.answer(**result)

            except ZeroDivisionError as e:
                print("ERROR")
                print(e)

        return wrapper

    return decorator
