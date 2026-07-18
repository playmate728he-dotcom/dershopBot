import asyncio

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

TOKEN = "8259954567:AAHEzRQz6qawRKshf6qAgA0Dknf6SEMniX0"

bot = Bot(TOKEN)
dp = Dispatcher()

countries = {
    "bangladesh": ("🇧🇩 Бангладеш", "800₸"),
    "usa": ("🇺🇸 США", "450₸"),
    "kazakhstan": ("🇰🇿 Казахстан", "1800₸"),
    "uzbekistan": ("🇺🇿 Узбекистан", "900₸"),
    "japan": ("🇯🇵 Япония", "2100₸"),
    "yemen": ("🇾🇪 Йемен", "500₸"),
    "india": ("🇮🇳 Индия", "300₸"),
    "france": ("🇫🇷 Франция", "1600₸"),
    "canada": ("🇨🇦 Канада", "450₸"),
    "kyrgyzstan": ("🇰🇬 Киргизия", "1600₸"),
    "germany": ("🇩🇪 Германия", "1600₸"),
}

main_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🌍 Каталог", callback_data="catalog")],
        [InlineKeyboardButton(text="💬 Поддержка", url="https://t.me/Der_shop")],
        [InlineKeyboardButton(text="ℹ️ О нас", callback_data="about")],
    ]
)

catalog_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🇧🇩 Бангладеш", callback_data="bangladesh")],
        [InlineKeyboardButton(text="🇺🇸 США", callback_data="usa")],
        [InlineKeyboardButton(text="🇰🇿 Казахстан", callback_data="kazakhstan")],
        [InlineKeyboardButton(text="🇺🇿 Узбекистан", callback_data="uzbekistan")],
        [InlineKeyboardButton(text="🇯🇵 Япония", callback_data="japan")],
        [InlineKeyboardButton(text="🇾🇪 Йемен", callback_data="yemen")],
        [InlineKeyboardButton(text="🇮🇳 Индия", callback_data="india")],
        [InlineKeyboardButton(text="🇫🇷 Франция", callback_data="france")],
        [InlineKeyboardButton(text="🇨🇦 Канада", callback_data="canada")],
        [InlineKeyboardButton(text="🇰🇬 Киргизия", callback_data="kyrgyzstan")],
        [InlineKeyboardButton(text="🇩🇪 Германия", callback_data="germany")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back")],
    ]
)


@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "🏠 <b>Добро пожаловать!</b>\n\nВыберите действие:",
        parse_mode="HTML",
        reply_markup=main_menu,
    )


@dp.callback_query(F.data == "catalog")
async def open_catalog(callback: CallbackQuery):
    await callback.message.edit_text(
        "🌍 <b>Выберите страну:</b>",
        parse_mode="HTML",
        reply_markup=catalog_menu,
    )


@dp.callback_query(F.data == "about")
async def about(callback: CallbackQuery):
    await callback.message.edit_text(
        "ℹ️ <b>О магазине</b>\n\n"
        "✅ Быстрая выдача\n"
        "💬 Поддержка: @Der_shop",
        parse_mode="HTML",
        reply_markup=main_menu,
    )


@dp.callback_query(F.data == "back")
async def back(callback: CallbackQuery):
    await callback.message.edit_text(
        "🏠 <b>Главное меню</b>",
        parse_mode="HTML",
        reply_markup=main_menu,
    )


@dp.callback_query(F.data.in_(countries.keys()))
async def show_country(callback: CallbackQuery):
    name, price = countries[callback.data]

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="💬 Купить",
                    url="https://t.me/Der_shop",
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ Назад",
                    callback_data="catalog",
                )
            ],
        ]
    )

    await callback.message.edit_text(
        f"{name}\n\n"
        f"💰 Цена: <b>{price}</b>\n\n"
        "📩 Для покупки нажмите кнопку ниже.",
        parse_mode="HTML",
        reply_markup=keyboard,
    )


async def main():
    print("Бот запускаеться...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())