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
import datetime

load_dotenv()

TOKEN = os.environ.get('TOKEN')
dev_status = bool(os.environ.get('DEVELOPING'))

link = 'https://t.me/NURlunchBot'
proxy_url = 'http://172.27.129.0:3128'
proxies = {'http': proxy_url, 'https': proxy_url}
date_mask = "%d-%m-%Y"

database_location = "database/app_database.db"

session = AiohttpSession(proxy=proxy_url)
if dev_status:
    print(f'dev status is {dev_status}, type is {type(dev_status)}')
    session = AiohttpSession()


ADMINS = ["kazamabeks", "nur_btuleev"]
dp = Dispatcher()

FIXED_PRICE_Lunch = 220
FIXED_PRICE_Bakery = 60
DEFAULT_AVAILABLE_AMOUNT = 100
MAX_TEXT_LENGTH = 25
#time limit for ordering and chaning order
hour_time_limit = 17
min_time_limit = 30
ORDER_TIME_LIMIT = datetime.time(hour_time_limit, min_time_limit)  # 11:00 AM
PAYMENT_TIME_LIMIT = datetime.time(hour_time_limit, min_time_limit)  # 11:00 AM

class EditLunchMenuState(StatesGroup):
    waiting_for_menu_text = State()

class EditBakeryMenuState(StatesGroup):
    waiting_for_menu_text = State()

class OrderLunchState(StatesGroup):
    selecting_lunch = State()
    confirming_order = State()

class OrderBakeryState(StatesGroup):
    selecting_bakery = State()
    confirming_order = State()


class BasketState(StatesGroup):
    viewing_basket = State()
    payment_in_basket = State()
    cash_or_card_qn = State()
    upload_receipt = State()

class AdditionsState(StatesGroup):
    'garnish'
    selecting_lunch = State()
    waiting_for_addition = State()

class ReviewState(StatesGroup):
    waiting_for_review = State()

class RaitingState(StatesGroup):
    selecting_lunch = State()
    set_raiting = State()

async def main() -> None:
    # Initialize Bot instance with default bot properties which will be passed to all API calls
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML), session=session)

    # And the run events dispatching
    await dp.start_polling(bot)






if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
