import aiogram

from aiogram import filters, types
from aiogram.fsm import scene, context
from dependency_injector.wiring import inject, Provide

from src.core import UserSession
from src.infrastructure.services import Translator
from src.infrastructure.services.rights_service import RightsService, Rights
from src.presentation import tools
from src.container import Container

category = "profile"


class MainScene(scene.Scene, state="profile"):

    @scene.on.message.enter()
    @scene.on.callback_query.enter()
    @tools.request_handler(auth=True, bypass_if_command=True, category=category)
    @inject
    async def default_handler(self, query: types.CallbackQuery or types.Message,
                              translator: Translator = Provide[Container.translator], user: UserSession = None):
        """(langs.translate("profile-text").format(
            user.Id,
            user.Nickname,
            user.Login if user.Login else "➖",
            "✅" if user.Password else "➖",
            await langs.translate(f"role-{user.Role.Name}", language=language),
            await langs.translate(f"rate-{user.Rate.Name}", language=language),
            user.PayedUntil.strftime(
                "%Y-%m-%d %H:%M:%S") if user.PayedUntil else "➖",
            user.JoinedAt.strftime(
                "%Y-%m-%d %H:%M:%S"),
            user.TelegramJoinedAt.strftime(
                "%Y-%m-%d %H:%M:%S")
        )"""

        text = translator.translate("profile-text").format(id=user.user_id,
                                                           nickname=user.data.nickname,
                                                           login=user.data.login,
                                                           role_name=translator.translate(f"role-{user.data.role.name}"),
                                                           rate_name=translator.translate(f"rate-{user.data.rate.name}",),
                                                           payed_until=user.data.payed_until if user.data.payed_until else "➖",
                                                           created_at=translator.date_to_text(user.data.created_at),
                                                           verification_status="✅" if user.data.is_verified else "➖")
        keyboard = [
            [types.InlineKeyboardButton(text=translator.translate("ui-tag-menu"), callback_data="menu")],
        ]

        return {"text": text, "reply_markup": types.InlineKeyboardMarkup(inline_keyboard=keyboard)}
