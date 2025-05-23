import aiogram
from dependency_injector.wiring import inject, Provide

from src import MailType
from src.container import Container
from src.core import Mail
from src.infrastructure.services import Translator

bot: aiogram.Bot = None


@inject
async def send_mail(mail: Mail, translator: Translator = Provide[Container.translator]) -> None:
    match mail.type:
        case MailType.RateExpired:
            title = translator.translate("hook-mail-preserved-rate_expired-title")
            content = translator.translate("hook-mail-preserved-rate_expired-content")
        case MailType.RateExpiration:
            title = translator.translate("hook-mail-preserved-rate_expiration-title").format(mail.extra_data.get("daysLeft"))
            content = translator.translate("hook-mail-preserved-rate_expiration-content").format(
                days_left=mail.extra_data.get("daysLeft"),
                rate_name=translator.translate(f"rate-{mail.extra_data.get('rateName')}"),
                rate_cost=mail.extra_data.get('needsToPay')
            )
        case _:
            title = mail.title,
            content = mail.content,

    keyboard = [
        [aiogram.types.InlineKeyboardButton(text=translator.translate("ui-tag-menu"), callback_data="menu")]
    ]

    text = translator.translate("hook-mail-verified-text" if mail.sender.is_verified else "hook-mail-text").format(
        sender=mail.sender.nickname,
        recipient=mail.recipient.nickname,
        title=title,
        content=content
    )

    await bot.send_message(mail.recipient.telegram_id, text=text, reply_markup=aiogram.types.InlineKeyboardMarkup(inline_keyboard=keyboard))
