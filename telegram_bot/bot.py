from aiogram import Bot, Dispatcher
from django.conf import settings
from .handlers import router


async def main():
    bot = Bot(token=settings.BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)