from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

replykeyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="pull")],
    ],
    resize_keyboard=True,
    input_field_placeholder="Use menu",
)
