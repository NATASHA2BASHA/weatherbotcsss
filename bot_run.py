from init_db import init
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from app.config import BOT_TOKEN
from app.handlers.commands import router
import asyncio
import logging
import aiocron
from app.database.models import SessionLocal, Subscription
from app.handlers.commands import get_forecast
from datetime import datetime

import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("weather.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
from app.handlers import commands
dp.include_router(commands.router)
from app.handlers import admin_panel
dp.include_router(admin_panel.router)
from app.handlers import commands


@aiocron.crontab("0 8,16,0 * * *")
async def send_daily_updates():
    db = SessionLocal()
    subs = db.query(Subscription).all()
    for sub in subs:
        try:
            if forecast:
                text = f"🌦 Прогноз погоды для {sub.city} (обновление):\n" + "\n".join(forecast)
                await bot.send_message(sub.user_id, text)
                logging.info(f"✅ Отправлен прогноз пользователю {sub.user_id} по городу {sub.city}")
                sub.last_sent = datetime.utcnow()
            else:
                logging.warning(f"⚠️ Пустой прогноз для {sub.city}")
        except Exception as e:
            logging.error(f"❌ Ошибка при отправке {sub.city} пользователю {sub.user_id}: {e}")
            logging.warning(f"⚠️ Пустой прогноз для {sub.city}")
        except Exception as e:
            logging.error(f"❌ Ошибка при отправке {sub.city} пользователю {sub.user_id}: {e}")
    db.commit()
    db.close()


init()

async def main():
    logging.info("Бот запускается...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())