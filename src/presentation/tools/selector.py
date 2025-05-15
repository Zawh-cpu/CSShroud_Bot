from aiogram.filters import callback_data

class Selector(callback_data.CallbackData, prefix="slr"):
    i: str = None


class IntSelector(callback_data.CallbackData, prefix="islr"):
    i: int = None


class OptSelector(callback_data.CallbackData, prefix="oslr"):
    i: str
    o: str