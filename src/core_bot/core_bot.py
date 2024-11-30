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
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

load_dotenv()

TOKEN = os.environ.get('TOKEN')
link = 'https://t.me/NURlunchBot'
# proxy_url = pass_decoder(os.environ.get(f'PROXY01'))
# proxies = {'http': proxy_url, 'https': proxy_url}
date_mask = "%d-%m-%Y"
# session = AiohttpSession(proxy=proxy_url)

database_location = "database/app_database.db"
session = AiohttpSession()

ADMINS = ["kazamabeks", "NUR_btuleev"]
dp = Dispatcher()

FIXED_PRICE = 220

class EditLunchMenuState(StatesGroup):
    waiting_for_menu_text = State()

class OrderLunchState(StatesGroup):
    selecting_lunch = State()
    confirming_order = State()
    # adding_comment = State()
    # waiting_for_comment = State()


class BasketState(StatesGroup):
    viewing_basket = State()

class AdditionsState(StatesGroup):
    'garnier'
    selecting_lunch = State()
    waiting_for_addition = State()
    # additions_to_specify = State()

class ReviewState(StatesGroup):
    waiting_for_review = State()

async def main() -> None:
    # Initialize Bot instance with default bot properties which will be passed to all API calls
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML), session=session)

    # And the run events dispatching
    await dp.start_polling(bot)






if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
