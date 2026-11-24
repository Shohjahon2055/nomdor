import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

import asyncio
from telegram_bot.bot import main

if __name__ == "__main__":
    asyncio.run(main())