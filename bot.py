import asyncio
import random


from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from config import TOKEN, ADMIN_ID, SHOP_USERNAME, STAR_RATE

from keyboards import (
    menu,
    stars_buy,
    admin_buttons,
    countries_keyboard,
    balance_keyboard,
)

from database import (
    create_db,
    add_user,
    get_balance,
    add_balance,
    get_cases,
    add_case,
    remove_case,
    add_country,
    get_inventory,
    remove_country,
    use_promo,
    create_promo,
)
from database import (
    create_promo,
    get_promo,
    activate_promo,
)
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext


class GiveBalance(StatesGroup):
    amount = State()


class Promo(StatesGroup):
    code = State()

bot = Bot(TOKEN)
dp = Dispatcher()




COUNTRIES = {
    "🇺🇸 США": 500,
    "🇰🇿 Казахстан": 1200,
    "🇺🇿 Узбекистан": 700,
    "🇩🇪 Германия": 1600,
    "🇯🇵 Япония": 1700,
    "🇰🇬 Киргизия": 1300,
    "🇹🇯 Таджикистан": 900,
    "🇹🇲 Туркменистан": 1200,
    "🇳🇱 Нидерланды": 600,
    "🇮🇳 Индия": 300,
    "🇮🇩 Индонезия": 300,
    "🇻🇳 Вьетнам": 600,
    "🇧🇩 Бангладеш": 500,
    "🇵🇰 Пакистан": 500,
    "🇵🇭 Филиппины": 500,
    "🇹🇭 Таиланд": 450,
    "🇪🇬 Египет": 500,
    "🇳🇬 Нигерия": 500,
    "🇩🇿 Алжир": 500,
    "🇾🇪 Йемен": 450,
    "🇹🇷 Турция": 700,
    "🇪🇹 Эфиопия": 450,
    "🇮🇷 Иран": 750,
    "🇨🇱 Чили": 500,
    "🇵🇱 Польша": 1850,
    "🇿🇦 Южная Африка": 1100,
    "🇵🇹 Португалия": 1200,
    "🇺🇦 Украина": 3000,
    "🇸🇦 Саудовская Аравия": 1500,
    "🇪🇸 Испания": 1800,
    "🇷🇴 Румыния": 400,
    "🇦🇺 Австралия": 1400,
    "🇨🇳 Китай": 10000,
}

CASE_REWARDS = {
    "🟢 Обычный": [
        "🇮🇳 Индия",
        "🇮🇩 Индонезия",
        "🇵🇰 Пакистан",
        "🇧🇩 Бангладеш",
        "🇻🇳 Вьетнам",
        "🇪🇹 Эфиопия",
        "🇹🇭 Таиланд",
        "🇪🇬 Египет",
    ],

    "🔵 Редкий": [
        "🇺🇸 США",
        "🇰🇿 Казахстан",
        "🇩🇪 Германия",
        "🇯🇵 Япония",
        "🇵🇹 Португалия",
        "🇵🇱 Польша",
        "🇹🇷 Турция",
    ],

    "🟣 Легендарный": [
        "🇨🇳 Китай",
        "🇺🇦 Украина",
        "🇪🇸 Испания",
        "🇦🇺 Австралия",
        "🇿🇦 Южная Африка",
        "🇸🇦 Саудовская Аравия",
    ]
}

@dp.message(CommandStart())
async def start(message: Message):

    await add_user(message.from_user.id)

    await message.answer(
        f"""
👋 Добро пожаловать в Der Shop!

⭐ Курс:
1⭐ = {STAR_RATE}₸

Выберите действие:
""",
        reply_markup=menu
    )


@dp.message(F.text == "👤 Профиль")
async def profile(message: Message):

    balance = await get_balance(message.from_user.id)
    cases = await get_cases(message.from_user.id)
    inventory = await get_inventory(message.from_user.id)

    await message.answer(
        f"""
👤 Ваш профиль

🆔 ID: {message.from_user.id}

💰 Баланс: {balance}₸

🎁 Кейсы: {cases}

🎒 Стран: {len(inventory)}
"""
    )


@dp.message(F.text == "🌍 Каталог")
async def catalog(message: Message):

    await message.answer(
        "🌍 Выберите страну:",
        reply_markup=countries_keyboard(COUNTRIES)
    )

@dp.message(lambda message: message.text in COUNTRIES)
async def buy_country(message: Message):

    country = message.text
    price = COUNTRIES[country]

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"💰 Купить за {price}₸",
                    callback_data=f"buy_money|{country}"
                )
            ],
            [
                InlineKeyboardButton(
                    text=f"⭐ Купить за Stars",
                    callback_data=f"buy_star|{country}"
                )
            ]
        ]
    )

    await message.answer(
        f"""
🌍 {country}

💰 Цена: {price}₸

Выберите способ оплаты:
""",
        reply_markup=keyboard
    )

@dp.callback_query(F.data.startswith("buy_money|"))
async def buy_money(callback: CallbackQuery):

    country = callback.data.split("|")[1]

    price = COUNTRIES[country]

    balance = await get_balance(callback.from_user.id)

    if balance < price:

        await callback.answer(
            "❌ Недостаточно средств!",
            show_alert=True
        )
        return

    await add_balance(callback.from_user.id, -price)

    await add_country(callback.from_user.id, country)

    await callback.message.edit_text(
        f"""✅ Покупка успешна!

🌍 {country}

💰 Списано: {price}₸"""
    )

    await callback.answer()


@dp.callback_query(F.data.startswith("buy_star|"))
async def buy_star(callback: CallbackQuery):

    country = callback.data.split("|")[1]
    price = COUNTRIES[country]

    stars = max(1, round(price / STAR_RATE))

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Выдать аккаунт",
                    callback_data=f"give|{callback.from_user.id}|{country}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="❌ Отклонить",
                    callback_data=f"deny_star|{callback.from_user.id}"
                )
            ]
        ]
    )

    await bot.send_message(
        ADMIN_ID,
        f"""
⭐ Новая заявка на покупку

👤 @{callback.from_user.username or 'без username'}
🆔 {callback.from_user.id}

🌍 Страна:
{country}

💰 Цена:
{price}₸

⭐ К оплате:
{stars} Stars

После получения Stars нажмите
«Выдать аккаунт».
""",
        reply_markup=keyboard
    )

    await callback.message.edit_text(
        f"""
✅ Заявка отправлена.

🌍 Страна:
{country}

⭐ К оплате:
{stars} Stars

После оплаты администратор выдаст аккаунт.
"""
    )

    await callback.answer()


@dp.message(F.text == "💳 Пополнить баланс")
async def balance(message: Message):

    await message.answer(
        """
💳 Пополнение баланса

Способ оплаты:
🏦 Kaspi.kz
  tekegram stars 
Для пополнения напишите:

👤 @Der_shop

После перевода нажмите кнопку ниже.

━━━━━━━━━━━━━━
⚠️ Баланс начисляется после проверки администратором.
""",
        reply_markup=balance_keyboard
    )

@dp.callback_query(F.data.startswith("give|"))
async def give_country(callback: CallbackQuery):

    _, user_id, country = callback.data.split("|")

    user_id = int(user_id)

    await add_country(user_id, country)

    await bot.send_message(
        user_id,
        f"""
🎉 Покупка завершена!

🌍 Вам выдана страна:

{country}

Спасибо за покупку ❤️
"""
    )

    await callback.message.edit_text("✅ Аккаунт выдан.")

    await callback.answer()

@dp.callback_query(F.data == "balance_paid")
async def balance_paid(callback: CallbackQuery):

    await bot.send_message(
        ADMIN_ID,
        f"""
🟢 Новая заявка на пополнение

👤 @{callback.from_user.username}
🆔 {callback.from_user.id}

Способ:
Kaspi.kz
""",
        reply_markup=admin_buttons
    )

    await callback.message.answer(
        """
✅ Заявка отправлена!

Ожидайте проверки администратора.

После подтверждения баланс будет начислен.
"""
    )

    await callback.answer()

@dp.callback_query(F.data == "approve")
async def approve(callback: CallbackQuery, state: FSMContext):

    user_id = int(callback.message.text.split("🆔 ")[1].split("\n")[0])

    await state.update_data(user_id=user_id)

    await callback.message.answer(
        "💰 Введите сумму пополнения в тенге:"
    )

    await state.set_state(GiveBalance.amount)

    await callback.answer()
    await callback.answer()


@dp.callback_query(F.data == "deny")
async def deny(callback: CallbackQuery):

    user_id = int(callback.message.text.split("🆔 ")[1].split("\n")[0])

    await bot.send_message(
        user_id,
        "❌ Ваша заявка отклонена."
    )

    await callback.message.edit_text("❌ Заявка отклонена.")

    await callback.answer()


@dp.message(GiveBalance.amount)
async def give_balance(message: Message, state: FSMContext):

    if not message.text.isdigit():
        await message.answer("Введите число.")
        return

    amount = int(message.text)

    data = await state.get_data()

    user_id = data["user_id"]

    await add_balance(user_id, amount)

    await bot.send_message(
        user_id,
        f"✅ Ваш баланс пополнен на {amount}₸!"
    )

    await message.answer("✅ Баланс успешно выдан.")

    await state.clear()

@dp.message(F.text == "🎁 Кейсы")
async def cases(message: Message):

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📦 Обычный — 600₸",
                    callback_data="case_normal"
                )
            ],
            [
                InlineKeyboardButton(
                    text="💎 Premium — 1500₸",
                    callback_data="case_premium"
                )
            ],
            [
                InlineKeyboardButton(
                    text="👑 VIP — 5000₸",
                    callback_data="case_vip"
                )
            ]
        ]
    )

    await message.answer(
        """
🎁 Кейсы

Выберите кейс для покупки.
""",
        reply_markup=keyboard
    )

CASE_PRICE = {
    "normal": 600,
    "premium": 1500,
    "vip": 5000,
}

CASE_CHANCE = {
    "normal": {
        "common": 94.50,
        "rare": 5.00,
        "legend": 0.45,
        "china": 0.05,
    },

    "premium": {
        "common": 75.00,
        "rare": 22.00,
        "legend": 2.70,
        "china": 0.30,
    },

    "vip": {
        "common": 45.00,
        "rare": 40.00,
        "legend": 14.00,
        "china": 1.00,
    }
}

COMMON = [
    "🇮🇳 Индия",
    "🇮🇩 Индонезия",
    "🇵🇰 Пакистан",
    "🇧🇩 Бангладеш",
    "🇻🇳 Вьетнам",
    "🇪🇹 Эфиопия",
    "🇹🇭 Таиланд",
    "🇪🇬 Египет",
    "🇳🇬 Нигерия",
    "🇩🇿 Алжир",
    "🇾🇪 Йемен",
    "🇨🇱 Чили",
]

RARE = [
    "🇺🇸 США",
    "🇰🇿 Казахстан",
    "🇺🇿 Узбекистан",
    "🇩🇪 Германия",
    "🇯🇵 Япония",
    "🇹🇷 Турция",
    "🇵🇹 Португалия",
    "🇵🇱 Польша",
    "🇷🇴 Румыния",
    "🇮🇷 Иран",
]

LEGEND = [
    "🇦🇺 Австралия",
    "🇪🇸 Испания",
    "🇿🇦 Южная Африка",
    "🇸🇦 Саудовская Аравия",
    "🇺🇦 Украина",
]

MYTH = [
    "🇨🇳 Китай",
]

@dp.callback_query(F.data.startswith("case_"))
async def buy_case(callback: CallbackQuery):

    case_type = callback.data.split("_")[1]

    price = CASE_PRICE[case_type]

    balance = await get_balance(callback.from_user.id)

    if balance < price:
        await callback.answer(
            "❌ Недостаточно средств.",
            show_alert=True
        )
        return

    await add_balance(callback.from_user.id, -price)
    await add_case(callback.from_user.id, 1)

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🎁 Открыть кейс",
                    callback_data=f"open_{case_type}"
                )
            ]
        ]
    )

    await callback.message.edit_text(
        f"""
✅ Вы купили кейс!

📦 Тип:
{case_type.upper()}

💰 Цена:
{price}₸
""",
        reply_markup=keyboard
    )

    await callback.answer()

@dp.callback_query(F.data.startswith("open_"))
async def open_case(callback: CallbackQuery):

    case_type = callback.data.split("_")[1]

    cases = await get_cases(callback.from_user.id)

    if cases <= 0:
        await callback.answer(
            "❌ У вас нет кейсов!",
            show_alert=True
        )
        return

    await remove_case(callback.from_user.id)

    await callback.message.edit_text("🎁 Открываем кейс...")
    await asyncio.sleep(1)

    await callback.message.edit_text("🎲 Крутим...")
    await asyncio.sleep(1)

    await callback.message.edit_text("✨ Определяем награду...")
    await asyncio.sleep(1)

    chance = CASE_CHANCE[case_type]

    roll = random.uniform(0, 100)

    if roll <= chance["china"]:
        rarity = "💎 Мифический"
        country = random.choice(MYTH)

    elif roll <= chance["china"] + chance["legend"]:
        rarity = "🟣 Легендарный"
        country = random.choice(LEGEND)

    elif roll <= chance["china"] + chance["legend"] + chance["rare"]:
        rarity = "🔵 Редкий"
        country = random.choice(RARE)

    else:
        rarity = "🟢 Обычный"
        country = random.choice(COMMON)

    await add_country(
        callback.from_user.id,
        country
    )

    await callback.message.edit_text(
        f"""
🎊 Кейс успешно открыт!

━━━━━━━━━━━━━━

⭐ Редкость:
{rarity}

🌍 Выпало:

{country}

🎉 Поздравляем!
"""
    )

    await callback.answer()

@dp.message(F.text == "🎒 Инвентарь")
async def inventory(message: Message):

    inv = await get_inventory(message.from_user.id)

    if not inv:
        await message.answer("🎒 Ваш инвентарь пуст.")
        return

    keyboard = []

    for row in inv:

        country = row[0]

        keyboard.append([
            InlineKeyboardButton(
                text=f"💸 Продать {country}",
                callback_data=f"sell|{country}"
            )
        ])

    await message.answer(
        "🎒 Ваш инвентарь:",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=keyboard
        )
    )

@dp.callback_query(F.data.startswith("sell|"))
async def sell_country(callback: CallbackQuery):

    country = callback.data.split("|")[1]

    if country not in COUNTRIES:
        await callback.answer(
            "❌ Ошибка.",
            show_alert=True
        )
        return

    price = COUNTRIES[country]

    reward = int(price * 0.7)  # 70% от стоимости

    await remove_country(
        callback.from_user.id,
        country
    )

    await add_balance(
        callback.from_user.id,
        reward
    )

    await callback.message.edit_text(
        f"""
💸 Страна успешно продана!

🌍 Страна:
{country}

💰 Получено:
{reward}₸

📈 Деньги зачислены на баланс.
"""
    )

    await callback.answer()

@dp.message(F.text == "🎟 Промокод")

@dp.message(Promo.code)
async def promo_check(message: Message, state: FSMContext):

    code = message.text.upper()

    promo = await get_promo(code)

    if not promo:
        await message.answer("❌ Промокод не найден.")
        await state.clear()
        return

    ok = await activate_promo(
        message.from_user.id,
        code
    )

    if not ok:
        await message.answer(
            "❌ Вы уже использовали этот промокод."
        )
        await state.clear()
        return

    reward = promo[1]
    reward_type = promo[2]
    uses = promo[3]

    if uses <= 0:
        await message.answer("❌ Промокод закончился.")
        await state.clear()
        return
        await use_promo(code)

    if reward_type == "money":
        await add_balance(
            message.from_user.id,
            reward
        )

        await message.answer(
            f"🎉 Промокод активирован!\n\n💰 Получено: {reward}₸"
        )

    elif reward_type == "case":
        await add_case(
            message.from_user.id,
            reward
        )

        await message.answer(
            f"🎉 Промокод активирован!\n\n🎁 Получено кейсов: {reward}"
        )

    await state.clear()

@dp.message(Command("createpromo"))
async def createpromo(message: Message):

    if message.from_user.id != ADMIN_ID:
        return

    args = message.text.split()

    if len(args) != 5:
        await message.answer(
            "Использование:\n"
            "/createpromo КОД НАГРАДА money/case ИСПОЛЬЗОВАНИЯ"
        )
        return

    code = args[1].upper()
    reward = int(args[2])
    reward_type = args[3].lower()
    uses = int(args[4])

    if reward_type not in ("money", "case"):
        await message.answer("Тип должен быть money или case.")
        return

    try:
        await create_promo(
            code,
            reward,
            reward_type,
            uses
        )

        await message.answer(
            f"""
✅ Промокод создан!

🎟 Код: {code}
🎁 Тип: {reward_type}
💰 Награда: {reward}
👥 Использований: {uses}
"""
        )

    except Exception as e:
        await message.answer(f"❌ Ошибка:\n{e}")
        
async def main():

    await create_db()

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())