import asyncio
import random
from datetime import datetime, timedelta
import aiohttp
from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from app.database.models import SessionLocal, Subscription
from app.config import WEATHER_API_KEY
import logging
from .states import ForecastState, DetailsState, SubscriptionState
from .keyboards import main_kb, menu_kb, subs_menu_kb, after_forecast_kb, favorites_kb

router = Router()

weather_reactions = {
    "ясно": [
        "Солнце греет — отличный день!",
        "Хорошая погода, можно и прогуляться!",
        "Ясно и спокойно — бери очки 😎",
        "Отличный повод выйти на улицу!"
    ],
    "дождь": [
        "Не забудь зонт — дождик идёт!",
        "Похоже, придётся укутаться в плащ.",
        "Мокрая погода — будь аккуратен на дороге.",
        "Самое время остаться дома с чаем ☕"
    ],
    "пасмурно": [
        "Серый день, но мы держимся 💪",
        "Пасмурно, но настроение можно сделать солнечным!",
        "Немного мрачно, но не критично.",
        "Такой день идеально подойдёт для книг и уюта."
    ],
    "снег": [
        "Время снежков и зимнего кайфа! ❄️",
        "Снег идёт — красиво, но скользко!",
        "Самое время горячего шоколада!",
        "Снежная сказка на улице!"
    ]
}

async def get_weather(city: str):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=ru"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                temp = data['main']['temp']
                desc = data['weather'][0]['description'].lower()
                return temp, desc
            return None, "Город не найден."

async def get_forecast(city: str, days: int = 3):
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=ru"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                result = []
                dates = set()
                for item in data['list']:
                    date = item['dt_txt'].split()[0]
                    if date not in dates and len(dates) < days:
                        dates.add(date)
                        result.append(f"{date}: {item['main']['temp']}°C, {item['weather'][0]['description']}")
                return "\n".join(result)
            return "Город не найден."

@router.message(Command("start"))
async def start_cmd(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Привет! Я бот прогноза погоды. Выберите действие:", reply_markup=main_kb)

@router.message(F.text == "Прогноз")
async def handle_forecast(message: Message, state: FSMContext):
    await state.set_state(ForecastState.waiting_for_city)
    await message.answer("Введите название города для прогноза:")

@router.message(F.text == "Подробности")
async def handle_details(message: Message, state: FSMContext):
    await state.set_state(DetailsState.waiting_for_city)
    await message.answer("Введите название города для прогноза на несколько дней:")

@router.message(F.text == "Подписки")
async def handle_subs(message: Message, state: FSMContext):
    await state.set_state(SubscriptionState.choosing_action)
    await message.answer("Меню подписок:", reply_markup=subs_menu_kb)

@router.message(F.text == "Подписаться")
async def subscribe_request(message: Message, state: FSMContext):
    await state.set_state(SubscriptionState.subscribing_city)
    await message.answer("Введите город для подписки:")

@router.message(F.text == "Отписаться")
async def unsubscribe_request(message: Message, state: FSMContext):
    await state.set_state(SubscriptionState.unsubscribing_city)
    await message.answer("Введите город, от которого хотите отписаться:")


@router.message(F.text == "Мои города")
async def my_cities(message: Message):
    db = SessionLocal()
    subs = db.query(Subscription).filter(Subscription.user_id == message.from_user.id).all()
    db.close()
    if not subs:
        await message.answer("У вас нет активных подписок.")
    else:
        cities = [s.city for s in subs]
        await message.answer("📍 Вы подписаны на:\n" + "\n".join(cities))
@router.message(F.text == "Назад")
async def go_back(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Вы вернулись в главное меню.", reply_markup=main_kb)

@router.message(Command("history"))
async def show_history(message: Message):
    await message.answer("Пока история прогнозов не реализована.")

@router.message(lambda message: message.text and not message.text.startswith('/'))
async def handle_input(message: Message, state: FSMContext):
    if message.text and message.text.startswith('/'):
        return
    db = SessionLocal()
    current_state = await state.get_state()

    if current_state == ForecastState.waiting_for_city.state:
        temp, desc = await get_weather(message.text)
        phrase = random.choice(weather_reactions.get(desc.split()[0], ["Погода интересная..."]))
        await message.answer(f"{message.text.capitalize()}: {temp}°C, {desc}\n{phrase}", reply_markup=main_kb)
        await state.clear()

    elif current_state == DetailsState.waiting_for_city.state:
        result = await get_forecast(message.text)
        await message.answer(result, reply_markup=main_kb)
        await state.clear()

    elif current_state == SubscriptionState.subscribing_city.state:
        db.add(Subscription(user_id=message.from_user.id, city=message.text))
        db.commit()
        await message.answer(f"Вы подписались на город {message.text}.", reply_markup=main_kb)
        await state.clear()

    elif current_state == SubscriptionState.unsubscribing_city.state:
        sub = db.query(Subscription).filter_by(user_id=message.from_user.id, city=message.text).first()
        if sub:
            db.delete(sub)
            db.commit()
            await message.answer(f"Вы отписались от города {message.text}.", reply_markup=main_kb)
        else:
            await message.answer(f"Вы не подписаны на {message.text}.", reply_markup=main_kb)
        await state.clear()

    db.close()


@router.message(SubscriptionState.subscribing_city)
async def process_subscribe_city(message: Message, state: FSMContext):
    city = message.text.strip()
    db = SessionLocal()
    existing = db.query(Subscription).filter_by(user_id=message.from_user.id, city=city).first()
    if not existing:
        db.add(Subscription(user_id=message.from_user.id, city=city))
        db.commit()
        await message.answer(f"✅ Подписка на город {city} оформлена.")
    else:
        await message.answer(f"⚠️ Вы уже подписаны на {city}.")
    db.close()
    await state.clear()


@router.message(SubscriptionState.unsubscribing_city)
async def process_unsubscribe_city(message: Message, state: FSMContext):
    city = message.text.strip()
    db = SessionLocal()
    sub = db.query(Subscription).filter_by(user_id=message.from_user.id, city=city).first()
    if sub:
        db.delete(sub)
        db.commit()
        await message.answer(f"❌ Вы отписались от города {city}.")
    else:
        await message.answer(f"⚠️ Вы не были подписаны на {city}.")
    db.close()
    await state.clear()

# Правка логики списка подписок

@router.message(F.text == "Мои города")
async def my_cities(message: Message):
    db = SessionLocal()
    subs = db.query(Subscription).filter(Subscription.user_id == message.from_user.id).all()
    db.close()
    if not subs:
        await message.answer("У вас нет активных подписок.")
    else:
        cities = [s.city for s in subs]
        await message.answer("📍 Вы подписаны на:\n" + "\n".join(cities))


