import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from config import TOKEN, ADMIN_ID, SHOP_USERNAME
from keyboards import menu, admin_buttons, balance_keyboard, catalog_keyboard, market_keyboard
from database import *

RUB_RATE = 6  # 1 RUB = 6 KZT
COUNTRIES = {
    "🇺🇸 США": 450, "🇰🇿 Казахстан": 990, "🇺🇿 Узбекистан": 700,
    "🇩🇪 Германия": 1200, "🇯🇵 Япония": 1300, "🇰🇬 Киргизия": 1100,
    "🇹🇯 Таджикистан": 900, "🇹🇲 Туркменистан": 1200, "🇳🇱 Нидерланды": 500,
    "🇮🇳 Индия": 300, "🇮🇩 Индонезия": 300, "🇻🇳 Вьетнам": 500,
    "🇧🇩 Бангладеш": 500, "🇵🇰 Пакистан": 500, "🇵🇭 Филиппины": 500,
    "🇹🇭 Таиланд": 450, "🇪🇬 Египет": 500, "🇳🇬 Нигерия": 500,
    "🇩🇿 Алжир": 500, "🇾🇪 Йемен": 450, "🇹🇷 Турция": 700,
    "🇪🇹 Эфиопия": 450, "🇮🇷 Иран": 500, "🇨🇱 Чили": 500,
    "🇵🇱 Польша": 1150, "🇿🇦 Южная Африка": 1100, "🇵🇹 Португалия": 1000,
    "🇺🇦 Украина": 1500, "🇸🇦 Саудовская Аравия": 990, "🇪🇸 Испания": 1500,
    "🇷🇴 Румыния": 400, "🇦🇺 Австралия": 1400, "🇨🇳 Китай": 10000,
}

class AddListing(StatesGroup):
    country = State(); price = State()
class MarketListing(StatesGroup):
    country = State(); price = State()
class Trade(StatesGroup):
    country = State(); target = State()
class GiveBalance(StatesGroup):
    user_id = State(); amount = State()
class TopUp(StatesGroup):
    currency = State(); amount = State()

bot = Bot(TOKEN)
dp = Dispatcher()

from aiogram import BaseMiddleware

class BanMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        uid = getattr(getattr(event, "from_user", None), "id", None)
        if uid and uid != ADMIN_ID:
            banned, reason = await get_ban(uid)
            if banned:
                try:
                    await event.answer(f"🚫 Вы заблокированы.\nПричина: {reason}")
                except Exception:
                    pass
                return
        return await handler(event, data)

dp.message.middleware(BanMiddleware())
dp.callback_query.middleware(BanMiddleware())
def rub(kzt):
    return round(kzt / RUB_RATE)

def admin(uid): return uid == ADMIN_ID

@dp.message(CommandStart())
async def start(message: Message):
    await add_user(message.from_user.id)
    await message.answer(f"👋 Der Shop\n\nКурс: 1 звезда = 10₸ / 1.5₽\n\nВыберите действие:", reply_markup=menu)

@dp.message(F.text == "👤 Профиль")
async def profile(message: Message):
    await add_user(message.from_user.id)
    b = await get_balance(message.from_user.id)
    inv = await get_inventory(message.from_user.id)
    await message.answer(f"👤 Профиль\n\n🆔 {message.from_user.id}\n💰 Баланс: {b}₽\n🎒 Аккаунтов: {len(inv)}")

@dp.message(F.text == "🌍 Каталог")
async def catalog(message: Message):
    # Официальный каталог: безлимитные позиции, цена задаётся админом.
    items = [{"id": k, "country": k, "price": v} for k, v in COUNTRIES.items()]
    await message.answer(
        "🌍 Официальный каталог\n\n"
        "♾ Безлимитные официальные позиции\n"
        "💱 1₽ = 6₸\n"
        "💎 1 звезда = 10₸ / 1.5₽",
        reply_markup=catalog_keyboard(items, RUB_RATE)
    )

@dp.callback_query(F.data.startswith("buy_catalog|"))
async def buy_catalog(c: CallbackQuery):
    country = c.data.split("|",1)[1]
    if country not in COUNTRIES:
        return await c.answer("❌ Страна не найдена.", show_alert=True)
    price_kzt = COUNTRIES[country]
    price_rub = rub(price_kzt)
    balance = await get_balance(c.from_user.id)
    if balance < price_rub:
        return await c.answer(f"❌ Нужно {price_rub}₽. Баланс: {balance}₽.", show_alert=True)
    await add_balance(c.from_user.id, -price_rub)
    await add_country(c.from_user.id, country)
    await c.message.edit_text(
        f"✅ Покупка успешна!\n\n🌍 {country}\n"
        f"💰 Цена: {price_kzt}₸ / {price_rub}₽\n"
        f"📩 Чтобы получить аккаунт, напишите @{SHOP_USERNAME}"
    )
    await bot.send_message(ADMIN_ID, f"🛒 Официальная продажа\n👤 Покупатель ID: {c.from_user.id}\n🌍 {country}\n💰 {price_rub}₽\nВыдать через @{SHOP_USERNAME}")
    await c.answer()

@dp.message(F.text == "🛒 Рынок")
async def market(message: Message):
    items = await get_market_listings()
    if not items: return await message.answer("🛒 Рынок пуст.")
    await message.answer("🛒 Публичный рынок:\n\nЦену устанавливают пользователи.", reply_markup=market_keyboard(items))

@dp.callback_query(F.data.startswith("market_buy|"))
async def market_buy(c: CallbackQuery):
    lid=int(c.data.split("|",1)[1]); item=await get_market_listing(lid)
    if not item: return await c.answer("❌ Лот уже продан.", show_alert=True)
    if item['user_id']==c.from_user.id: return await c.answer("❌ Нельзя купить свой лот.", show_alert=True)
    if await get_balance(c.from_user.id) < item['price']: return await c.answer("❌ Недостаточно рублей.", show_alert=True)
    if not await remove_market_listing(lid): return await c.answer("❌ Лот уже продан.", show_alert=True)
    await add_balance(c.from_user.id, -item['price']); await add_balance(item['user_id'], item['price'])
    await c.message.edit_text(f"✅ Покупка успешна!\n\n🌍 {item['country']}\n💰 {item['price']}₽\n\n📩 Чтобы получить аккаунт, напишите @{SHOP_USERNAME}")
    await bot.send_message(item['user_id'], f"🛒 Ваш аккаунт продан!\n🌍 {item['country']}\n💰 Получено: {item['price']}₽")
    await bot.send_message(ADMIN_ID, f"🛒 Рынок\nПродавец ID: {item['user_id']}\nПокупатель ID: {c.from_user.id}\n🌍 {item['country']}\n💰 {item['price']}₽")
    await c.answer()

@dp.message(F.text == "🎒 Инвентарь")
async def inventory(message: Message):
    inv=await get_inventory(message.from_user.id)
    if not inv: return await message.answer("🎒 Инвентарь пуст.")
    rows=[]
    for country in [x[0] for x in inv]:
        official=rub(COUNTRIES.get(country,0))
        rows += [[InlineKeyboardButton(text=f"🏷 Официально — {official}₽ (-35%)", callback_data=f"official|{country}")],
                 [InlineKeyboardButton(text=f"🛒 На рынок — {country}", callback_data=f"market_start|{country}" )],
                 [InlineKeyboardButton(text=f"🤝 Трейд — {country}", callback_data=f"trade_start|{country}" )]]
    await message.answer("🎒 Инвентарь:\n\n🏷 Официально: комиссия 35%\n🛒 Рынок: свою цену устанавливаете сами\n🤝 Трейд: бесплатно", reply_markup=InlineKeyboardMarkup(inline_keyboard=rows))

@dp.callback_query(F.data.startswith("official|"))
async def official(c: CallbackQuery):
    country=c.data.split("|",1)[1]; inv=await get_inventory(c.from_user.id)
    if not any(x[0]==country for x in inv): return await c.answer("❌ Нет в инвентаре.", show_alert=True)
    gross=rub(COUNTRIES.get(country,0)); payout=round(gross*0.65)
    await remove_country(c.from_user.id,country); await add_balance(c.from_user.id,payout)
    await c.message.edit_text(f"✅ Официально продано\n🌍 {country}\n💰 Получено: {payout}₽\n📉 Комиссия: 35%")

@dp.callback_query(F.data.startswith("market_start|"))
async def market_start(c: CallbackQuery,state:FSMContext):
    country=c.data.split("|",1)[1]
    if not any(x[0]==country for x in await get_inventory(c.from_user.id)): return await c.answer("❌ Нет в инвентаре.",show_alert=True)
    await state.update_data(country=country); await state.set_state(MarketListing.price)
    await c.message.answer(f"🛒 {country}\nВведите цену в ₽ (только целое число):"); await c.answer()

@dp.message(MarketListing.price)
async def market_price(m:Message,state:FSMContext):
    if not m.text.isdigit() or int(m.text)<=0: return await m.answer("Введите положительное целое число ₽.")
    country=(await state.get_data())['country']
    if not any(x[0]==country for x in await get_inventory(m.from_user.id)): return await m.answer("❌ Аккаунта уже нет.")
    await remove_country(m.from_user.id,country); lid=await add_market_listing(m.from_user.id,country,int(m.text)); await state.clear()
    await m.answer(f"✅ Выставлено на рынок!\n#{lid}\n🌍 {country}\n💰 {int(m.text)}₽\n👀 Видят все пользователи.")

@dp.callback_query(F.data.startswith("market_remove|"))
async def market_remove(c:CallbackQuery):
    lid=int(c.data.split("|",1)[1]); item=await get_market_listing(lid)
    if not item or item['user_id']!=c.from_user.id: return await c.answer("❌ Лот не найден.",show_alert=True)
    await remove_market_listing(lid); await add_country(c.from_user.id,item['country']); await c.message.edit_text("✅ Лот снят, аккаунт возвращён в инвентарь.")

@dp.callback_query(F.data.startswith("trade_start|"))
async def trade_start(c:CallbackQuery,state:FSMContext):
    country=c.data.split("|",1)[1]
    if not any(x[0]==country for x in await get_inventory(c.from_user.id)): return await c.answer("❌ Нет в инвентаре.",show_alert=True)
    await state.update_data(country=country); await state.set_state(Trade.target)
    await c.message.answer(f"🤝 Трейд: {country}\nВведите Telegram ID получателя:"); await c.answer()

@dp.message(Trade.target)
async def trade_target(m:Message,state:FSMContext):
    if not m.text.isdigit(): return await m.answer("Введите Telegram ID числом.")
    target=int(m.text)
    if target==m.from_user.id: return await m.answer("❌ Нельзя трейдить самому себе.")
    country=(await state.get_data())['country']
    if not any(x[0]==country for x in await get_inventory(m.from_user.id)): return await m.answer("❌ Аккаунта уже нет.")
    tid=await add_trade(m.from_user.id,target,country)
    kb=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="✅ Принять",callback_data=f"trade_accept|{tid}"),InlineKeyboardButton(text="❌ Отклонить",callback_data=f"trade_decline|{tid}")]])
    try: await bot.send_message(target,f"🤝 Трейд\n\n👤 От ID: {m.from_user.id}\n🌍 Вам предлагают: {country}",reply_markup=kb)
    except Exception: return await m.answer("❌ Пользователь должен сначала открыть бота (/start).")
    await m.answer("✅ Предложение отправлено."); await state.clear()

@dp.callback_query(F.data.startswith("trade_accept|"))
async def trade_accept(c:CallbackQuery):
    tid=int(c.data.split("|",1)[1]); t=await get_trade(tid)
    if not t or t['status']!='pending' or t['receiver_id']!=c.from_user.id: return await c.answer("❌ Трейд недоступен.",show_alert=True)
    if not any(x[0]==t['sender_country'] for x in await get_inventory(t['sender_id'])): await update_trade_status(tid,'cancelled'); return await c.answer("❌ У отправителя уже нет аккаунта.",show_alert=True)
    await remove_country(t['sender_id'],t['sender_country']); await add_country(c.from_user.id,t['sender_country']); await update_trade_status(tid,'accepted')
    await c.message.edit_text(f"✅ Трейд принят!\n🌍 {t['sender_country']}"); await bot.send_message(t['sender_id'],f"✅ Трейд принят пользователем {c.from_user.id}.\n🌍 {t['sender_country']}"); await c.answer()

@dp.callback_query(F.data.startswith("trade_decline|"))
async def trade_decline(c:CallbackQuery):
    tid=int(c.data.split("|",1)[1]); t=await get_trade(tid)
    if not t or t['status']!='pending' or t['receiver_id']!=c.from_user.id: return await c.answer("❌ Трейд недоступен.",show_alert=True)
    await update_trade_status(tid,'declined'); await c.message.edit_text("❌ Трейд отклонён."); await bot.send_message(t['sender_id'],"❌ Ваш трейд отклонён."); await c.answer()

@dp.message(F.text == "💳 Пополнить баланс")
async def topup(m:Message):
    await m.answer(
        "💳 Пополнение баланса\n\n"
        "Выберите валюту пополнения:",
        reply_markup=balance_keyboard
    )

@dp.callback_query(F.data.startswith("topup_currency|"))
async def topup_currency(c:CallbackQuery, state:FSMContext):
    currency=c.data.split("|",1)[1]
    if currency not in ("₽","₸","⭐","🎁 NFT"):
        return await c.answer("❌ Неизвестная валюта.",show_alert=True)
    await state.update_data(currency=currency)
    await state.set_state(TopUp.amount)
    await c.message.answer(f"💳 Пополнение: {currency}\n\nВведите сумму пополнения:")
    await c.answer()

@dp.message(TopUp.amount)
async def topup_amount(m:Message,state:FSMContext):
    if not m.text or not m.text.isdigit() or int(m.text)<=0:
        return await m.answer("❌ Введите положительное целое число.")
    amount=int(m.text)
    currency=(await state.get_data())["currency"]
    await bot.send_message(
        ADMIN_ID,
        f"💳 Новая заявка на пополнение\n\n"
        f"👤 ID: {m.from_user.id}\n"
        f"💰 Сумма: {amount}{currency}\n"
        f"📩 Клиент: @{SHOP_USERNAME}"
    )
    await m.answer(
        f"✅ Заявка на пополнение оформлена!\n\n"
        f"💰 Сумма: {amount}{currency}\n\n"
        f"Спасибо! Напишите @{SHOP_USERNAME} для оплаты."
    )
    await state.clear()

@dp.message(F.text == "➕ Выставить аккаунт")
async def admin_add(m:Message,state:FSMContext):
    if not admin(m.from_user.id): return
    await m.answer("Введите страну из списка:\n"+"\n".join(COUNTRIES)); await state.set_state(AddListing.country)

@dp.message(AddListing.country)
async def admin_country(m:Message,state:FSMContext):
    if m.text not in COUNTRIES: return await m.answer("Выберите страну из списка.")
    await state.update_data(country=m.text); await state.set_state(AddListing.price); await m.answer(f"Введите цену в ₸ для {m.text}.")

@dp.message(AddListing.price)
async def admin_price(m:Message,state:FSMContext):
    if not m.text.isdigit() or int(m.text)<=0: return await m.answer("Введите число.")
    d=await state.get_data(); price=int(m.text); COUNTRIES[d['country']]=price; await state.clear(); await m.answer(f"✅ Официальная цена изменена: {d['country']} — {price}₸ / {rub(price)}₽\n♾ Теперь позиция доступна безлимитно в каталоге.")

@dp.message(F.text.regexp(r'^/delete\s+\d+\s+\d+$'))
async def admin_delete_balance(m: Message):
    if not admin(m.from_user.id):
        return
    uid, amount = map(int, m.text.split()[1:])
    balance = await get_balance(uid)
    if amount <= 0 or amount > balance:
        return await m.answer(f"❌ Нельзя снять {amount}₽. Баланс пользователя: {balance}₽.")
    await add_balance(uid, -amount)
    await m.answer(f"✅ С баланса {uid} снято {amount}₽. Новый баланс: {balance-amount}₽.")
    try: await bot.send_message(uid, f"⚠️ С вашего баланса снято {amount}₽. Новый баланс: {balance-amount}₽.")
    except Exception: pass

@dp.message(F.text.regexp(r'^/ban\s+\d+\s+.+$'))
async def admin_ban(m: Message):
    if not admin(m.from_user.id): return
    parts=m.text.split(maxsplit=2); uid=int(parts[1]); reason=parts[2].strip()
    if uid==ADMIN_ID: return await m.answer("❌ Нельзя забанить администратора.")
    await set_ban(uid,True,reason); await m.answer(f"🔨 Пользователь {uid} забанен.\nПричина: {reason}")
    try: await bot.send_message(uid,f"🚫 Вы заблокированы.\nПричина: {reason}")
    except Exception: pass

@dp.message(F.text.regexp(r'^/unban\s+\d+$'))
async def admin_unban(m: Message):
    if not admin(m.from_user.id): return
    uid=int(m.text.split()[1]); await set_ban(uid,False,''); await m.answer(f"✅ Пользователь {uid} разблокирован.")

@dp.message(F.text.startswith("/give"))
async def admin_give(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    parts = message.text.split()
    if len(parts) != 3 or not parts[1].isdigit() or not parts[2].isdigit():
        await message.answer("Использование: /give ID сумма")
        return

    user_id = int(parts[1])
    amount = int(parts[2])

    if amount <= 0:
        await message.answer("❌ Сумма должна быть больше 0.")
        return

    await add_balance(user_id, amount)

    await message.answer(
        f"✅ Баланс пополнен.\n\n"
        f"👤 ID: {user_id}\n"
        f"💰 Выдано: {amount}₽"
    )

    try:
        await bot.send_message(
            user_id,
            f"💰 Вам зачислено {amount}₽ на баланс."
        )
    except Exception:
        pass



async def main():
    await create_db(); await dp.start_polling(bot)

if __name__ == '__main__': asyncio.run(main())
