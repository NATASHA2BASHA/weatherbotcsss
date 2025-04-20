
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Прогноз"), KeyboardButton(text="Подробности")],
        [KeyboardButton(text="Подписки"), KeyboardButton(text="Мои города")]
    ],
    resize_keyboard=True
)

menu_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Выбрать город")],
        [KeyboardButton(text="Назад")]
    ],
    resize_keyboard=True
)

subs_menu_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Подписаться")],
        [KeyboardButton(text="Отписаться")],
        [KeyboardButton(text="Назад")]
    ],
    resize_keyboard=True
)

after_forecast_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Добавить в избранное")],
        [KeyboardButton(text="Назад")]
    ],
    resize_keyboard=True
)

favorites_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Удалить город")],
        [KeyboardButton(text="Назад")]
    ],
    resize_keyboard=True
)
