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
# time limit for ordering and chaning order
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


translation_dict = {
    "im_a_cutomer_str": {
        "en": "🙋‍♂️ I'm a customer",
        "ru": "🙋‍♂️ Я клиент",
        "ky": "🙋‍♂️ Мен кардармын"
    },
    "im_admin_str": {
        "en": "🛠️ I'm an administrator",
        "ru": "🛠️ Я администратор",
        "ky": "🛠️ Мен админмин"
    },
    "main_menu_str": {
        "en": "📍 Main menu",
        "ru": "📍 Главное меню",
        "ky": "📍 Башкы меню"
    },
    "order_lunch_str": {
        "en": "🍽️ Order a lunch",
        "ru": "🍽️ Заказать обед",
        "ky": "🍽️ Түшкү тамак заказ кылуу"
    },
    "garnish_str": {
        "en": "➕ Specify additions",
        "ru": "➕ Указать добавки",
        "ky": "➕ Кошумчаларды тандоо"
    },
    "my_orders_str": {
        "en": "🛒 My orders",
        "ru": "🛒 Мои заказы",
        "ky": "🛒 Менин заказдарым"
    },
    "lunch_rating_list_str": {
        "en": "⭐ Lunch rating list",
        "ru": "⭐ Рейтинг обедов",
        "ky": "⭐ Түшкү тамактардын рейтинги"
    },
    "rate_lunch_str": {
        "en": "👍 Rate your lunch",
        "ru": "👍 Оцените обед",
        "ky": "👍 Түшкү тамагыңарды баалагыла"
    },
    "leave_review_str": {
        "en": "📝 Leave a review",
        "ru": "📝 Оставить отзыв",
        "ky": "📝 Пикир калтыруу"
    },
    "current_lunch_menu_str": {
        "en": "📜 Current Lunch Menu",
        "ru": "📜 Текущее меню",
        "ky": "📜 Азыркы түшкү тамак менюсу"
    },
    "reset_lunch_menu_str": {
        "en": "🔄 Reset Lunch Menu",
        "ru": "🔄 Сбросить меню",
        "ky": "🔄 Түшкү тамак менюсун өчүрүү"
    },
    "export_today_data_str": {
        "en": "📤 Export today's data",
        "ru": "📤 Экспорт данных за сегодня",
        "ky": "📤 Бүгүнкү маалыматты экспорттоо"
    },
    "export_all_data_str": {
        "en": "📦 Export all data",
        "ru": "📦 Экспорт всех данных",
        "ky": "📦 Бардык маалыматты экспорттоо"
    },
    # admin one
    "reset_lunch_menu_str": {
        "en": "🔄 Reset Lunch Menu",
        "ru": "🔄 Сбросить меню",
        "ky": "🔄 Түшкү тамак менюсун тазалоо"
    },
    "export_today_data_str": {
        "en": "📤 Export today's data",
        "ru": "📤 Экспорт данных за сегодня",
        "ky": "📤 Бүгүнкү маалыматты экспорттоо"
    },
    "export_all_data_str": {
        "en": "📦 Export all data",
        "ru": "📦 Экспорт всех данных",
        "ky": "📦 Бардык маалыматты экспорттоо"
    },

}

user_languages = {}
default_lang = 'ky'  # // en //ru


def get_translation(key: str, lang: str) -> str:
    return translation_dict.get(key, {}).get(lang, key)


async def main() -> None:
    # Initialize Bot instance with default bot properties which will be passed to all API calls
    bot = Bot(token=TOKEN, default=DefaultBotProperties(
        parse_mode=ParseMode.HTML), session=session)

    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
