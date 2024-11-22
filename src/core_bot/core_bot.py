import asyncio
import logging
import sys
from os import getenv

from aiogram import Bot, Dispatcher, html, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import *
# from nurtelecom_gras_library import pass_decoder
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, ContentType
import os
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.client.session.aiohttp import AiohttpSession
from dotenv import load_dotenv
import sqlite3

load_dotenv()

TOKEN = os.environ.get('TOKEN')
link = 'https://t.me/NURlunchBot'
# proxy_url = pass_decoder(os.environ.get(f'PROXY01'))
# proxies = {'http': proxy_url, 'https': proxy_url}

# session = AiohttpSession(proxy=proxy_url)
session = AiohttpSession()

ADMINS = ["kazamabeks", "NUR_btuleev"]
dp = Dispatcher()




async def main() -> None:
    # Initialize Bot instance with default bot properties which will be passed to all API calls
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML), session=session)

    # And the run events dispatching
    await dp.start_polling(bot)






if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
