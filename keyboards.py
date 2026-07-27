from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="👤 Профиль"),
            KeyboardButton(text="🌍 Каталог"),
        ],
        [
            KeyboardButton(text="🎒 Инвентарь"),
            KeyboardButton(text="🎁 Кейсы"),
        ],
        [
            KeyboardButton(text="💳 Пополнить баланс"),
            KeyboardButton(text="📈 Апгрейд"),
        ],
        [
            KeyboardButton(text="🎟 Промокод"),
        ],
    ],
    resize_keyboard=True,
)

# Кнопка покупки за Stars
stars_buy = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="⭐ Я оплатил",
                callback_data="stars_buy",
            )
        ]
    ]
)

# Кнопки для админа
admin_buttons = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="✅ Выдать",
                callback_data="approve",
            ),
            InlineKeyboardButton(
                text="❌ Отклонить",
                callback_data="deny",
            ),
        ]
    ]
)


def countries_keyboard(countries: dict):
    buttons = []

    for country, price in countries.items():
        buttons.append([KeyboardButton(text=country)])

    buttons.append([KeyboardButton(text="🔙 Назад")])

    return ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
    )

balance_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="⭐ Я оплатил",
                callback_data="balance_paid"
            )
        ]
    ]
)