import asyncio
from email import message
import random


from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from config import *
from database import *

# ensure delete_item is defined (some static analyzers may not detect star-imports)
try:
    # re-import explicitly to satisfy linters/static checkers
    from database import delete_item  # type: ignore
except Exception:
    async def delete_item(item_id):
        # fallback no-op if database does not provide it
        return None

BOT_TOKEN = "8259954567:AAEZf5Io0ycwnoo_ZLtpnwnCJfOdB_7hR8g"

bot = Bot(BOT_TOKEN)
dp = Dispatcher()


COUNTRIES = {
    "usa": ("🇺🇸 США", 500),
    "kazakhstan": ("🇰🇿 Казахстан", 1600),
    "uzbekistan": ("🇺🇿 Узбекистан", 900),
    "germany": ("🇩🇪 Германия", 1600),
    "japan": ("🇯🇵 Япония", 2000),

    "kyrgyzstan": ("🇰🇬 Киргизия", 1500),
    "tajikistan": ("🇹🇯 Таджикистан", 1000),
    "turkmenistan": ("🇹🇲 Туркменистан", 1500),
    "serbia": ("🇷🇸 Сербия", 1600),
    "netherlands": ("🇳🇱 Нидерланды", 890),

    "india": ("🇮🇳 Индия", 400),
    "indonesia": ("🇮🇩 Индонезия", 500),
    "vietnam": ("🇻🇳 Вьетнам", 670),
    "bangladesh": ("🇧🇩 Бангладеш", 550),
    "pakistan": ("🇵🇰 Пакистан", 540),

    "philippines": ("🇵🇭 Филиппины", 490),
    "thailand": ("🇹🇭 Таиланд", 490),
    "egypt": ("🇪🇬 Египет", 500),
    "nigeria": ("🇳🇬 Нигерия", 500),
    "algeria": ("🇩🇿 Алжир", 500),

    "yemen": ("🇾🇪 Йемен", 450),
    "turkey": ("🇹🇷 Турция", 700),
}


MAIN_MENU = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="👤 Профиль", callback_data="profile")],
        [InlineKeyboardButton(text="🌍 Каталог", callback_data="catalog")],
        [InlineKeyboardButton(text="🎁 Кейсы", callback_data="cases")],
        [InlineKeyboardButton(text="📦 Инвентарь", callback_data="inventory")],
        [InlineKeyboardButton(text="⬆️ Апгрейд", callback_data="upgrade")],
        [InlineKeyboardButton(text="🎯 Квесты", callback_data="quests")],
        [InlineKeyboardButton(text="🎟 Промокод", callback_data="promo")],
        [InlineKeyboardButton(text="💬 Поддержка", url=SUPPORT)],
    ]
)


@dp.message(CommandStart())
async def start(message: Message):

    await add_user(
        message.from_user.id,
        message.from_user.username or ""
    )

    await message.answer(
        "<b>🏪 Добро пожаловать в Der Shop!</b>\n\n"
        "Выберите нужный раздел.",
        parse_mode="HTML",
        reply_markup=MAIN_MENU
    )


@dp.callback_query(F.data == "menu")
async def menu(callback: CallbackQuery):

    await callback.message.edit_text(
        "<b>🏪 Главное меню</b>\n\n"
        "Выберите нужный раздел.",
        parse_mode="HTML",
        reply_markup=MAIN_MENU
    )


@dp.callback_query(F.data == "profile")
async def profile(callback: CallbackQuery):

    balance = await get_balance(callback.from_user.id)
    xp = await get_xp(callback.from_user.id)
    level = await get_level(callback.from_user.id)

    pepe, samsa, der = await get_cases(callback.from_user.id)

    text = f"""
👤 <b>Профиль</b>

🆔 ID:
<code>{callback.from_user.id}</code>

💰 Баланс:
<b>{balance}₸</b>

🏆 Уровень:
<b>{level}</b>

⭐ XP:
<b>{xp}/{LEVEL_XP}</b>

🎁 Кейсы:

🟢 Pepe — <b>{pepe}</b>

🟡 Самса — <b>{samsa}</b>

🔴 Der Der — <b>{der}</b>
"""

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📦 Инвентарь",
                    callback_data="inventory"
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ Назад",
                    callback_data="menu"
                )
            ]
        ]
    )

    await callback.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=keyboard
    )
@dp.callback_query(F.data == "catalog")
async def catalog(callback: CallbackQuery):

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔥 Популярные",
                    callback_data="popular"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🌍 Все страны",
                    callback_data="all"
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ Назад",
                    callback_data="menu"
                )
            ]
        ]
    )

    await callback.message.edit_text(
        "<b>🌍 Каталог аккаунтов</b>\n\n"
        "Выберите раздел.",
        parse_mode="HTML",
        reply_markup=keyboard
    )


@dp.callback_query(F.data == "popular")
async def popular(callback: CallbackQuery):

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🇺🇸 США • 500₸", callback_data="country_usa")],
            [InlineKeyboardButton(text="🇰🇿 Казахстан • 1600₸", callback_data="country_kazakhstan")],
            [InlineKeyboardButton(text="🇺🇿 Узбекистан • 900₸", callback_data="country_uzbekistan")],
            [InlineKeyboardButton(text="🇩🇪 Германия • 1600₸", callback_data="country_germany")],
            [InlineKeyboardButton(text="🇯🇵 Япония • 2000₸", callback_data="country_japan")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="catalog")]
        ]
    )

    await callback.message.edit_text(
        "<b>🔥 Популярные аккаунты</b>",
        parse_mode="HTML",
        reply_markup=keyboard
    )


@dp.callback_query(F.data == "all")
async def all_countries(callback: CallbackQuery):

    keyboard = []

    for code, (name, price) in COUNTRIES.items():
        keyboard.append([
            InlineKeyboardButton(
                text=f"{name} • {price}₸",
                callback_data=f"country_{code}"
            )
        ])

    keyboard.append([
        InlineKeyboardButton(
            text="⬅️ Назад",
            callback_data="catalog"
        )
    ])

    await callback.message.edit_text(
        "<b>🌍 Все страны</b>",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=keyboard
        )
    )
@dp.callback_query(F.data.startswith("country_"))
async def country(callback: CallbackQuery):

    code = callback.data.replace("country_", "")

    if code not in COUNTRIES:
        return

    name, price = COUNTRIES[code]

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="💰 Купить за баланс",
                    callback_data=f"buy_{code}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="⭐ Купить за Stars",
                    url=SUPPORT
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬆️ Апгрейд",
                    callback_data=f"upgrade_{code}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ Назад",
                    callback_data="catalog"
                )
            ]
        ]
    )

    await callback.message.edit_text(
        f"""
{name}

💰 Цена:
<b>{price}₸</b>

⭐ Stars:
Напишите админу после оплаты.

👤 @Der_shop
""",
        parse_mode="HTML",
        reply_markup=keyboard
    )


@dp.callback_query(F.data.startswith("buy_"))
async def buy_country(callback: CallbackQuery):

    code = callback.data.replace("buy_", "")

    if code not in COUNTRIES:
        return

    name, price = COUNTRIES[code]

    balance = await get_balance(callback.from_user.id)

    if balance < price:

        await callback.answer(
            "❌ Недостаточно средств.",
            show_alert=True
        )
        return

    await add_balance(
        callback.from_user.id,
        -price
    )

    await add_country(
        callback.from_user.id,
        name,
        price
    )

    await add_xp(
        callback.from_user.id,
        XP_FOR_BUY
    )

    xp = await get_xp(callback.from_user.id)
    level = await get_level(callback.from_user.id)

    if xp >= LEVEL_XP:

        await set_level(
            callback.from_user.id,
            level + 1
        )

    await callback.message.edit_text(
        f"""
✅ Покупка успешна!

🌍 {name}

💸 Списано:
<b>{price}₸</b>

⭐ +100 XP
""",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="📦 Инвентарь",
                        callback_data="inventory"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="⬅️ Меню",
                        callback_data="menu"
                    )
                ]
            ]
        )
    )
@dp.callback_query(F.data == "inventory")
async def inventory(callback: CallbackQuery):

    items = await get_inventory(callback.from_user.id)

    if not items:

        await callback.message.edit_text(
            """
📦 <b>Инвентарь пуст.</b>

Купите первую страну в каталоге.
""",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="🌍 Каталог",
                            callback_data="catalog"
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="⬅️ Меню",
                            callback_data="menu"
                        )
                    ]
                ]
            )
        )
        return

    keyboard = []

    for item_id, country, price in items:

        keyboard.append([
            InlineKeyboardButton(
                text=f"{country} • {price}₸",
                callback_data=f"inv_{item_id}"
            )
        ])

    keyboard.append([
        InlineKeyboardButton(
            text="⬅️ Меню",
            callback_data="menu"
        )
    ])

    await callback.message.edit_text(
        "📦 <b>Ваш инвентарь</b>",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=keyboard
        )
    )


@dp.callback_query(F.data.startswith("inv_"))
async def inventory_item(callback: CallbackQuery):

    item_id = int(callback.data.replace("inv_", ""))

    item = await get_item(item_id)

    if item is None:
        return

    _, _, country, price = item

    sell_price = int(price * 0.65)

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"💸 Продать за {sell_price}₸",
                    callback_data=f"sell_{item_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬆️ Апгрейд",
                    callback_data=f"upgrade_item_{item_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ Назад",
                    callback_data="inventory"
                )
            ]
        ]
    )

    await callback.message.edit_text(
        f"""
📦 <b>{country}</b>

💰 Цена:

{price}₸

💸 Продажа:

{sell_price}₸
""",
        parse_mode="HTML",
        reply_markup=keyboard
    )

@dp.callback_query(F.data.startswith("sell_"))
async def sell(callback: CallbackQuery):

    item_id = int(callback.data.replace("sell_", ""))

    reward = await sell_item(item_id)

    if reward is False:
        return

    await callback.message.edit_text(
        f"""
✅ Продано!

💰 Получено:

<b>{reward}₸</b>
""",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="📦 Инвентарь",
                        callback_data="inventory"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="🏠 Меню",
                        callback_data="menu"
                    )
                ]
            ]
        )
    )

# ==========================
# 🎁 КЕЙСЫ
# ==========================

@dp.callback_query(F.data == "cases")
async def cases_menu(callback: CallbackQuery):

    pepe, samsa, der = await get_cases(callback.from_user.id)

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"🟢 Pepe ({pepe})",
                    callback_data="case_pepe"
                )
            ],
            [
                InlineKeyboardButton(
                    text=f"🟡 Самса ({samsa})",
                    callback_data="case_samsa"
                )
            ],
            [
                InlineKeyboardButton(
                    text=f"🔴 Der Der ({der})",
                    callback_data="case_der"
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ Назад",
                    callback_data="menu"
                )
            ]
        ]
    )

    await callback.message.edit_text(
        """
🎁 <b>Кейсы</b>

🟢 Pepe — 500₸ / ⭐50

🟡 Самса — 750₸ / ⭐75

🔴 Der Der — 1500₸ / ⭐150

⭐ Для покупки за Stars
напишите администратору.
""",
        parse_mode="HTML",
        reply_markup=keyboard
    )


@dp.callback_query(F.data == "case_pepe")
async def case_pepe(callback: CallbackQuery):

    await callback.message.edit_text(
        """
🟢 <b>Pepe Case</b>

Стоимость:

💰 500₸

⭐ 50 Stars

После оплаты Stars
напишите @Der_shop
""",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="💰 Купить за баланс",
                        callback_data="buy_case_pepe"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="⭐ Купить за Stars",
                        url=SUPPORT
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="🎁 Открыть",
                        callback_data="open_pepe"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="⬅️ Назад",
                        callback_data="cases"
                    )
                ]
            ]
        )
    )
@dp.callback_query(F.data == "buy_case_pepe")
async def buy_case_pepe(callback: CallbackQuery):

    ok = await buy_case_balance(
        callback.from_user.id,
        PEPE_PRICE
    )

    if not ok:

        await callback.answer(
            "❌ Недостаточно средств!",
            show_alert=True
        )
        return

    await add_case(
        callback.from_user.id,
        "pepe",
        1
    )

    await callback.answer(
        "🟢 Pepe кейс куплен!"
    )

    await cases_menu(callback)


@dp.callback_query(F.data == "open_pepe")
async def open_pepe(callback: CallbackQuery):

    pepe, samsa, der = await get_cases(callback.from_user.id)

    if pepe <= 0:

        await callback.answer(
            "❌ У вас нет Pepe кейсов.",
            show_alert=True
        )
        return

    await remove_case(
        callback.from_user.id,
        "pepe"
    )

    country = random.choice(
        
        list(COUNTRIES.values())
    )

    name = country[0]
    price = country[1]

    await add_country(
        callback.from_user.id,
        name,
        price
    )

    await add_xp(
        callback.from_user.id,
        XP_FOR_CASE
    )

    await callback.message.edit_text(
        f"""
🎉 Кейс открыт!

Вам выпало:

{name}

💰 Стоимость:

<b>{price}₸</b>
""",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="📦 Инвентарь",
                        callback_data="inventory"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="🎁 Кейсы",
                        callback_data="cases"
                    )
                ]
            ]
        )
    )
# ==========================
# 🟡 SAMSA
# ==========================

@dp.callback_query(F.data == "buy_case_samsa")
async def buy_case_samsa(callback: CallbackQuery):

    ok = await buy_case_balance(
        callback.from_user.id,
        SAMSA_PRICE
    )

    if not ok:
        await callback.answer("❌ Недостаточно средств!", show_alert=True)
        return

    await add_case(callback.from_user.id, "samsa", 1)

    await callback.answer("🟡 Самса кейс куплен!")

    await cases_menu(callback)


@dp.callback_query(F.data == "open_samsa")
async def open_samsa(callback: CallbackQuery):

    pepe, samsa, der = await get_cases(callback.from_user.id)

    if samsa <= 0:
        await callback.answer("❌ Нет Самса кейсов!", show_alert=True)
        return

    await remove_case(callback.from_user.id, "samsa")

    country = random.choice(list(COUNTRIES.values()))

    await add_country(
        callback.from_user.id,
        country[0],
        country[1]
    )

    await add_xp(callback.from_user.id, XP_FOR_CASE)

    await callback.message.edit_text(
        f"""
🎉 Самса кейс открыт!

Выпало:

{country[0]}

💰 Цена:

<b>{country[1]}₸</b>
""",
        parse_mode="HTML"
    )


# ==========================
# 🔴 DER DER
# ==========================

@dp.callback_query(F.data == "buy_case_der")
async def buy_case_der(callback: CallbackQuery):

    ok = await buy_case_balance(
        callback.from_user.id,
        DER_PRICE
    )

    if not ok:
        await callback.answer("❌ Недостаточно средств!", show_alert=True)
        return

    await add_case(callback.from_user.id, "der", 1)

    await callback.answer("🔴 Der Der кейс куплен!")

    await cases_menu(callback)


@dp.callback_query(F.data == "open_der")
async def open_der(callback: CallbackQuery):

    pepe, samsa, der = await get_cases(callback.from_user.id)

    if der <= 0:
        await callback.answer("❌ Нет Der Der кейсов!", show_alert=True)
        return

    await remove_case(callback.from_user.id, "der")

    country = random.choice(list(COUNTRIES.values()))

    await add_country(
        callback.from_user.id,
        country[0],
        country[1]
    )

    await add_xp(callback.from_user.id, XP_FOR_CASE)

    await callback.message.edit_text(
        f"""
🎉 Der Der кейс открыт!

Выпало:

{country[0]}

💰 Цена:

<b>{country[1]}₸</b>
""",
        parse_mode="HTML"
    )
UPGRADE_ITEM = {}
UPGRADE_TARGET = {}


@dp.callback_query(F.data.startswith("country_"))
async def upgrade_target(callback: CallbackQuery):

    if callback.from_user.id not in UPGRADE_ITEM:
        return

    code = callback.data.replace("country_", "")

    if code not in COUNTRIES:
        return

    item = await get_item(
        UPGRADE_ITEM[callback.from_user.id]
    )

    if item is None:
        return

    item_id, user_id, old_country, old_price = item

    new_country, new_price = COUNTRIES[code]

    if new_price <= old_price:

        await callback.answer(
            "❌ Можно улучшать только на более дорогую страну.",
            show_alert=True
        )
        return

    chance = round((old_price / new_price) * 100)

    if chance > 95:
        chance = 95

    if chance < 5:
        chance = 5

    UPGRADE_TARGET[callback.from_user.id] = code

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⬆️ Начать апгрейд",
                    callback_data="upgrade_start"
                )
            ],
            [
                InlineKeyboardButton(
                    text="❌ Отмена",
                    callback_data="menu"
                )
            ]
        ]
    )

    await callback.message.edit_text(
        f"""
⬆️ <b>Апгрейд</b>

📦 Было:
{old_country}
({old_price}₸)

🎯 Цель:
{new_country}
({new_price}₸)

🎲 Шанс:

<b>{chance}%</b>
""",
        parse_mode="HTML",
        reply_markup=keyboard
    )
@dp.callback_query(F.data == "upgrade_start")
async def upgrade_start(callback: CallbackQuery):

    if callback.from_user.id not in UPGRADE_ITEM:
        return


    if callback.from_user.id not in UPGRADE_TARGET:
        return
    item = await get_item(
        UPGRADE_ITEM[callback.from_user.id]
    )

    if item is None:
        return

    item_id, user_id, old_country, old_price = item

    code = UPGRADE_TARGET[callback.from_user.id]

    new_country, new_price = COUNTRIES[code]

    chance = round((old_price / new_price) * 100)

    if chance > 95:
        chance = 95

    if chance < 5:
        chance = 5

    roll = random.randint(1, 100)

    await delete_item(item_id)

    if roll <= chance:

        await add_country(
            callback.from_user.id,
            new_country,
            new_price
        )

        await callback.message.edit_text(
            f"""
🎉 <b>АПГРЕЙД УДАЛСЯ!</b>

📦 Было:

{old_country}

⬆️ Стало:

{new_country}

🎲 Шанс:

{chance}%

✅ Выпало:

{roll}
""",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="📦 Инвентарь",
                            callback_data="inventory"
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="⬅️ Меню",
                            callback_data="menu"
                        )
                    ]
                ]
            )
        )

    else:

        await callback.message.edit_text(
            f"""
💥 <b>АПГРЕЙД НЕ УДАЛСЯ</b>

📦

{old_country}

сгорел...

🎲 Шанс:

{chance}%

❌ Выпало:

{roll}
""",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="📦 Инвентарь",
                            callback_data="inventory"
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="⬅️ Меню",
                            callback_data="menu"
                        )
                    ]
                ]
            )
        )

    UPGRADE_ITEM.pop(callback.from_user.id, None)
    UPGRADE_TARGET.pop(callback.from_user.id, None)

# ==========================
# 👑 АДМИН
# ==========================

from aiogram.filters import Command


@dp.message(Command("givebalance"))
async def give_balance(message: Message):

    if message.from_user.id != ADMIN_ID:
        return

    args = message.text.split()

    if len(args) != 3:
        await message.answer(
            "Использование:\n/givebalance ID сумма"
        )
        return

    user_id = int(args[1])
    amount = int(args[2])

    await add_balance(user_id, amount)

    await message.answer("✅ Баланс выдан.")
    @dp.message(Command("givecase"))
    async def give_case(message: Message):

     if message.from_user.id != ADMIN_ID:
        return

    args = message.text.split()

    if len(args) != 4:
        await message.answer(
            "Использование:\n"
            "/givecase ID pepe 3"
        )
        return

    user_id = int(args[1])
    case_type = args[2].lower()
    amount = int(args[3])

    if case_type not in ["pepe", "samsa", "der"]:
        await message.answer(
            "Кейс должен быть:\n"
            "pepe\n"
            "samsa\n"
            "der"
        )
        return

    await add_case(
        user_id,
        case_type,
        amount
    )

    await message.answer(
        "✅ Кейсы успешно выданы."
    )
@dp.message(Command("givecountry"))
async def give_country(message: Message):

    if message.from_user.id != ADMIN_ID:
        return

    args = message.text.split()

    if len(args) != 3:
        await message.answer(
            "Использование:\n"
            "/givecountry ID usa"
        )
        return

    user_id = int(args[1])
    code = args[2].lower()

    if code not in COUNTRIES:
        await message.answer("❌ Такой страны нет.")
        return

    country, price = COUNTRIES[code]

    await add_country(
        user_id,
        country,
        price
    )

    await message.answer(
        f"✅ Выдано:\n{country}"
    )
PROMO_WAIT = set()
BROADCAST_WAIT = set()
@dp.callback_query(F.data == "promo")
async def promo(callback: CallbackQuery):

    PROMO_WAIT.add(callback.from_user.id)

    await callback.message.edit_text(
        "🎟 Введите промокод сообщением."
    )
@dp.message()
async def promo_message(message: Message):

    if message.from_user.id not in PROMO_WAIT:
        return

    PROMO_WAIT.remove(message.from_user.id)

    result = await activate_promo(
        message.from_user.id,
        message.text.strip()
    )

    if result == "notfound":
        await message.answer("❌ Промокод не найден.")
        return

    if result == "used":
        await message.answer("❌ Вы уже использовали этот промокод.")
        return

    if result == "ended":
        await message.answer("❌ Промокод закончился.")
        return

    await add_balance(
        message.from_user.id,
        result
    )

    await message.answer(
        f"✅ Вы получили {result}₸!"
    )
@dp.message(Command("createpromo"))
async def createpromo(message: Message):

    if message.from_user.id != ADMIN_ID:
        return

    args = message.text.split()

    if len(args) != 4:
        await message.answer(
            "/createpromo CODE 500 10"
        )
        return

    code = args[1]

    reward = int(args[2])

    uses = int(args[3])

    await create_promo(
        code,
        reward,
        uses
    )

    await message.answer("✅ Промокод создан.")

@dp.message(Command("stats"))
async def stats(message: Message):

    if message.from_user.id != ADMIN_ID:
        return

    users, inventory, balance, pepe, samsa, der = await get_stats()

    await message.answer(
        f"""
📊 <b>Статистика Der Shop</b>

👥 Пользователей:
<b>{users}</b>

🌍 Стран:
<b>{inventory}</b>

💰 Общий баланс:
<b>{balance}₸</b>

🎁 Кейсы:

🟢 Pepe:
<b>{pepe}</b>

🟡 Самса:
<b>{samsa}</b>

🔴 Der Der:
<b>{der}</b>
""",
        parse_mode="HTML"
    )
@dp.message(Command("broadcast"))

async def broadcast(message: Message):

    if message.from_user.id != ADMIN_ID:
        return

    BROADCAST_WAIT.add(message.from_user.id)

    await message.answer(
        "📢 Отправьте сообщение для рассылки."
    )
    @dp.message()
    async def broadcast_send(message: Message):

     if message.from_user.id not in BROADCAST_WAIT:
        return

    BROADCAST_WAIT.remove(message.from_user.id)

    users = await get_all_users()

    ok = 0
    bad = 0

    for user in users:

        try:

            await bot.send_message(
                user[0],
                message.html_text,
                parse_mode="HTML"
            )

            ok += 1

        except:

            bad += 1

    await message.answer(
        f"""
✅ Рассылка завершена.

📨 Отправлено:
<b>{ok}</b>

❌ Ошибок:
<b>{bad}</b>
""",
        parse_mode="HTML"
    )
import asyncio

async def main():
    await create_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())