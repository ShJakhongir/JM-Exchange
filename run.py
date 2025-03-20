import asyncio 
import logging

from aiogram import Bot, Dispatcher, F
from config import TOKEN
from app.handlers import router
from app.database.db import init_db

bot = Bot(token=TOKEN)
dp = Dispatcher()

async def main():
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == '__main__':
    init_db()
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')



