from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

menu = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="👤 Профиль"), KeyboardButton(text="🌍 Каталог")],
    [KeyboardButton(text="🛒 Рынок"), KeyboardButton(text="🎒 Инвентарь")],
    [KeyboardButton(text="💳 Пополнить баланс"), KeyboardButton(text="🎁 Кейсы")],
], resize_keyboard=True)

admin_buttons = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="✅ Выдать",callback_data="approve"),InlineKeyboardButton(text="❌ Отклонить",callback_data="deny")]])
balance_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🇷🇺 Рубли ₽", callback_data="topup_currency|₽")],
    [InlineKeyboardButton(text="🇰🇿 Тенге ₸", callback_data="topup_currency|₸")],
    [InlineKeyboardButton(text="⭐ Stars", callback_data="topup_currency|⭐")],
    [InlineKeyboardButton(text="🎁 NFT", callback_data="topup_currency|🎁 NFT")],
])

def catalog_keyboard(items, rate=6):
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=f"{x['country']} — {x['price']}₸ / {round(x['price']/rate)}₽",callback_data=f"buy_catalog|{x['id']}")] for x in items])

def market_keyboard(items):
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=f"🌍 {x['country']} — {x['price']}₽",callback_data=f"market_buy|{x['id']}")] for x in items])
