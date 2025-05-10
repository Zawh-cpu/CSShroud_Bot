from aiogram.filters import callback_data

class Selector(callback_data.CallbackData, prefix="slctr"):
    i: str = None


class IntSelector(callback_data.CallbackData, prefix="islctr"):
    i: int = None