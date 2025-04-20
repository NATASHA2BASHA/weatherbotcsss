from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from app.database.models import SessionLocal, Subscription
import logging
from datetime import datetime

router = Router()
ADMIN_IDS = [519154593]

admin_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🟢 Статус бота", callback_data="admin_status")],
    [InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats")],
    [InlineKeyboardButton(text="👥 Пользователи", callback_data="admin_users")],
    [InlineKeyboardButton(text="🗑️ Выход", callback_data="admin_exit")],
])

@router.message(Command("admin"))
async def admin_panel(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        return await message.answer("⛔ У вас нет доступа к админ‑панели.")
    await message.answer("🛠 Админ‑панель", reply_markup=admin_kb)

@router.callback_query(F.data == "admin_status")
async def admin_status(callback: CallbackQuery):
    await callback.answer()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    text = f"🟢 Бот активен\nТекущее время: {now}"
    await callback.message.edit_text(text, reply_markup=admin_kb)

@router.callback_query(F.data == "admin_stats")
async def admin_stats(callback: CallbackQuery):
    await callback.answer()
    with SessionLocal() as session:
        user_count = session.query(Subscription.user_id).distinct().count()
        city_count = session.query(Subscription.city).count()
    text = f"📊 Статистика:\n👥 Пользователей: {user_count}\n🏙 Подписок: {city_count}"
    await callback.message.edit_text(text, reply_markup=admin_kb)

@router.callback_query(F.data == "admin_users")
async def admin_users(callback: CallbackQuery):
    await callback.answer()
    with SessionLocal() as session:
        user_ids = [u[0] for u in session.query(Subscription.user_id).distinct().all()]
    text = "👥 Пользователи:\n" + "\n".join(str(uid) for uid in user_ids)
    await callback.message.edit_text(text, reply_markup=admin_kb)

@router.callback_query(F.data == "admin_exit")
async def admin_exit(callback: CallbackQuery):
    await callback.answer("Выход из панели.")
    await callback.message.delete()
