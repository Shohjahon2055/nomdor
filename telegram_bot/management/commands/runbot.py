import asyncio
from django.core.management.base import BaseCommand
from telegram_bot.bot import main


class Command(BaseCommand):
    help = "Telegram botni ishga tushiradi"

    def handle(self, *args, **options):
        asyncio.run(main())