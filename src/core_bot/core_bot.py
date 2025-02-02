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


ADMINS = ["kazamabeks", "nur_btuleev"]  # "nur_btuleev"
dp = Dispatcher()

FIXED_PRICE_Lunch = 220
FIXED_PRICE_Bakery = 60
DEFAULT_AVAILABLE_AMOUNT = 100
MAX_TEXT_LENGTH = 25
# time limit for ordering and chaning order
hour_time_limit = 14
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
    'hello_string': {
        "en": "👋 Hi, {}! Welcome to NUR Lunch Bot! \n\nPlease select an option below.\nTo change language, press:\n\n/ky Кыргызча\n\n/ru Русский\n\n/en English",
        "ru": "👋 Привет, {}! Добро пожаловать в NUR Lunch Bot! \n\nВыберите действие ниже.\nДля смены языка нажмите:\n\n/ky Кыргызча\n\n/ru Русский\n\n/en English",
        "ky": "👋 Салам, {}! NUR Lunch Bot'ко кош келиңиз! \n\nТөмөндөгү параметрлерди тандаңыз.\nТилди өзгөртүү үчүн басыңыз:\n\n/ky Кыргызча\n\n/ru Русский\n\n/en English"
    },

    'lier_string': {
        "en": "🚫 {}, you are not an administrator!",
        "ru": "🚫 {}, вы не администратор!",
        "ky": "🚫 {}, сиз администратор эмессиз!"
    },
    # text part

    'debt_btn_str': {
        "en": "💰 Debt: {} KGS",
        "ru": "💰 Долг: {} KGS",
        "ky": "💰 Карыз: {} KGS"
    },
    'total_btn_str': {
        "en": "💵 Total: {} KGS",
        "ru": "💵 Всего: {} KGS",
        "ky": "💵 Жалпы: {} KGS"
    },
    'make_payment_btn_str': {
        "en": "💳 Make a payment",
        "ru": "💳 Оплатить",
        "ky": "💳 Төлөм жүргүзүү"
    },
    'your_basket_info_str': {
        "en": "🍽️ Your basket for {}:",
        "ru": "🍽️ Ваша корзина на {}:",
        "ky": "🍽️ Сиздин себетиңиз {}:"
    },
    'have_unpaid_orders_info_str': {
        "en": "⚠️ You have unpaid orders {}.",
        "ru": "⚠️ У вас есть неоплаченные заказы {}.",
        "ky": "⚠️ Сизде төлөнбөгөн заказдар бар {}."
    },
    'have_paid_orders_info_str': {
        "en": "✅ Total paid for {}: {} KGS",
        "ru": "✅ Итого оплачено за {}: {} KGS",
        "ky": "✅ {} үчүн төлөнгөн сумма: {} KGS"
    },
    'order_paid_info_str': {
        "en": "🟢 Your order for {} is paid",
        "ru": "🟢 Ваш заказ за {} оплачен",
        "ky": "🟢 Сиздин {} үчүн заказ төлөндү"
    },
    'empty_basket_info_str': {
        "en": "⚠️ Your basket is empty for {}.",
        "ru": "⚠️ Ваша корзина пуста на {}.",
        "ky": "⚠️ Сиздин себетиңиз бош {}."
    },
    #
    'customer_menu_options_str': {
        "en": "📋 Choose an option",
        "ru": "📋 Выберите действие",
        "ky": "📋 Тандоо жасаңыз"
    },
    'delete_orders_time_warning_str': {
        "en": "⏳ Time is over! You can delete orders only before {}:{}",
        "ru": "⏳ Время вышло! Удалять заказы можно только до {}:{}",
        "ky": "⏳ Убакыт бүттү! Заказды {}:{} чейин гана өчүрсө болот"
    },
    'item_removed_str': {
        "en": "✅ Item removed from basket.",
        "ru": "✅ Товар удален из корзины.",
        "ky": "✅ Товар себеттен өчүрүлдү."
    },
    'item_not_found_str': {
        "en": "❌ Item not found in your basket.",
        "ru": "❌ Товар не найден в вашей корзине.",
        "ky": "❌ Себетте мындай товар жок."
    },
    'payment_time_warning_str': {
        "en": "⏳ You can pay only after {}:{}",
        "ru": "⏳ Оплата возможна только после {}:{}",
        "ky": "⏳ Төлөмдү {}:{} кийин гана жүргүзүүгө болот"
    },
    'select_payment_method_str': {
        "en": "💰 Select a payment method:",
        "ru": "💰 Выберите способ оплаты:",
        "ky": "💰 Төлөм ыкмасын тандаңыз:"
    },
    'pay_cash_str': {
        "en": "💵 Cash",
        "ru": "💵 Наличные",
        "ky": "💵 Накталай"
    },
    'pay_card_str': {
        "en": "💳 Card",
        "ru": "💳 Карта",
        "ky": "💳 Карт"
    },
    'cash_payment_complete_str': {
        "en": "✅ Payment completed with cash. Thank you!",
        "ru": "✅ Оплата наличными завершена. Спасибо!",
        "ky": "✅ Накталай төлөм ийгиликтүү жүргүзүлдү. Рахмат!"
    },
    'upload_photo_receipt_str': {
        "en": "📸 Please upload a photo of your receipt.",
        "ru": "📸 Пожалуйста, загрузите фото чека.",
        "ky": "📸 Касса чегинин сүрөтүн жүктөңүз."
    },
    'error_upload_photo_str': {
        "en": "❌ Please upload a valid photo or file.",
        "ru": "❌ Пожалуйста, загрузите корректное фото или файл.",
        "ky": "❌ Туура сүрөт же файл жүктөңүз."
    },
    'success_upload_photo_str': {
        "en": "✅ Receipt uploaded successfully. Thank you for your payment!",
        "ru": "✅ Чек успешно загружен. Спасибо за оплату!",
        "ky": "✅ Чек ийгиликтүү жүктөлдү. Төлөм үчүн рахмат!"
    },
    'cancel_upload_photo_str': {
        "en": "❌ Upload process has been canceled.",
        "ru": "❌ Загрузка отменена.",
        "ky": "❌ Жүктөө токтотулду."
    },
    # tested above
    'order_time_warning_str': {
        "en": "⏳ Order time is over! You can do it only before {}:{}",
        "ru": "⏳ Время заказа вышло! Можно сделать только до {}:{}",
        "ky": "⏳ Заказ алуу убактысы бүттү! Аны {}:{} чейин гана жасаса болот"
    },
    'add_garnish_str': {
        "en": "🍽️ Please type the garnish for {}",
        "ru": "🍽️ Укажите гарнир для {}",
        "ky": "🍽️ {} үчүн гарнир жазыңыз"
    },
    'confirm_garnish_str': {
        "en": "✅ Additional info for {} has been updated. Thank you!",
        "ru": "✅ Дополнительная информация для {} обновлена. Спасибо!",
        "ky": "✅ {} үчүн кошумча маалымат жаңыртылды. Рахмат!"
    },
    'select_following_options_str': {
        "en": "📌 Choose the following:",
        "ru": "📌 Выберите из списка:",
        "ky": "📌 Төмөнкүлөрдү тандаңыз:"
    },
    'canceled_str': {
        "en": "❌ Action canceled!",
        "ru": "❌ Действие отменено!",
        "ky": "❌ Иш-аракет жокко чыгарылды!"
    },
    # tested above
    'available_lunch_info_str': {
        "en": "🍴 Select your lunch option for {}:",
        "ru": "🍴 Выберите обед на {}:",
        "ky": "🍴 {} үчүн түшкү тамакты тандаңыз:"
    },
    'no_lunch_info_str': {
        "en": "⚠️ No lunch options available for {}:",
        "ru": "⚠️ Обедов нет на {}:",
        "ky": "⚠️ {} үчүн түшкү тамак жеткиликтүү эмес:"
    },
    'yes_str': {
        "en": "✅ Yes",
        "ru": "✅ Да",
        "ky": "✅ Ооба"
    },
    'no_str': {
        "en": "❌ No",
        "ru": "❌ Нет",
        "ky": "❌ Жок"
    },
    'add_to_basket_qn_str': {
        "en": "🛒 Would you like to add '{}' to your basket?",
        "ru": "🛒 Добавить '{}' в корзину?",
        "ky": "🛒 '{}' себетке кошууну каалайсызбы?"
    },
    'item_not_found_generic_str': {
        "en": "❌ Item not found",
        "ru": "❌ Товар не найден",
        "ky": "❌ Товар табылган жок"
    },
    'out_of_stock_warning_str': {
        "en": "⚠️ Not enough stock available for '{}'. Only {} left.",
        "ru": "⚠️ Недостаточно товара '{}'. Осталось всего {}.",
        "ky": "⚠️ '{}' жетишсиз. Калган саны: {}."
    },
    'item_added_to_basket_str': {
        "en": "✅ {}x {} has been added to your basket.\nRemaining stock: {}",
        "ru": "✅ {}x {} добавлен(ы) в корзину.\nОстаток: {}",
        "ky": "✅ {}x {} себетке кошулду.\nКалган запасы: {}"
    },
    # tested above
    'rate_time_warning_str': {
        "en": "⏳ You can rate only after {}:{}",
        "ru": "⏳ Оценивать можно только после {}:{}",
        "ky": "⏳ Баалоо {}:{} кийин гана мүмкүн"
    },
    'bad_rating_str': {
        "en": "👎 Bad",
        "ru": "👎 Плохо",
        "ky": "👎 Начар"
    },
    'good_rating_str': {
        "en": "🙂 Good",
        "ru": "🙂 Хорошо",
        "ky": "🙂 Жакшы"
    },
    'awesome_rating_str': {
        "en": "😍 Awesome",
        "ru": "😍 Отлично",
        "ky": "😍 Сонун"
    },
    'rate_item_str': {
        "en": "⭐ Please rate **{}**:",
        "ru": "⭐ Оцените **{}**:",
        "ky": "⭐ **{}** баалаңыз:"
    },
    'no_item_for_rating_str': {
        "en": "❌ No item selected for rating.",
        "ru": "❌ Товар для оценки не выбран.",
        "ky": "❌ Баалоо үчүн товар тандалган жок."
    },
    'rating_complete_str': {
        "en": "✅ Thank you for your rating! You rated **{}** with {} ⭐.",
        "ru": "✅ Спасибо за вашу оценку! Вы поставили **{}** {} ⭐.",
        "ky": "✅ Баа бергениңиз үчүн рахмат! Сиз **{}** {} ⭐ менен бааладыңыз."
    },
    'top_lunch_listing_str': {
        "en": "📊 TOP Lunch Items (Last 30 Days):",
        "ru": "📊 ТОП обеды (за последние 30 дней):",
        "ky": "📊 Акыркы 30 күндөгү ТОП түшкү тамактар:"
    },
    'no_top_lunch_listing_str': {
        "en": "⚠️ No ratings available in the last 30 days.",
        "ru": "⚠️ За последние 30 дней нет оценок.",
        "ky": "⚠️ Акыркы 30 күндө баалоо болгон жок."
    },
    # tested above
    'type_review_str': {
        "en": "📝 Please type your review:",
        "ru": "📝 Пожалуйста, напишите ваш отзыв:",
        "ky": "📝 Сураныч, пикириңизди жазыңыз:"
    },

    'review_registered_str': {
        "en": "✅ Thank you for your review! 🙏",
        "ru": "✅ Спасибо за ваш отзыв! 🙏",
        "ky": "✅ Пикириңиз үчүн рахмат! 🙏"
    },

    'failed_review_registered_str': {
        "en": "❌ Failed to save your review. Error:",
        "ru": "❌ Не удалось сохранить ваш отзыв. Ошибка:",
        "ky": "❌ Пикириңизди сактоо мүмкүн болгон жок. Ката:"
    },
    # tested above
    'reset_lunch_menu_info_str': {
        "en": "📋 Please send the lunch menu details in the format: stock name price: \n50 Manty 250\n30 Pasta 300\nBurger 500",
        "ru": "📋 Отправьте детали меню в формате: количество название цена: \n50 Манты 250\n30 Паста 300\nБургер 500",
        "ky": "📋 Түшкү меню маалыматтарын төмөнкү форматта жөнөтүңүз: саны аталышы баасы: \n50 Манты 250\n30 Паста 300\nБургер 500"
    },

    'error_empty_given_menu_str': {
        "en": "❌ The provided menu is empty. Please provide a valid menu.",
        "ru": "❌ Предоставленное меню пусто. Пожалуйста, отправьте корректное меню.",
        "ky": "❌ Берилген меню бош. Туура меню жазыңыз."
    },

    'menu_successfully_updated_str': {
        "en": "✅ Menu updated for {}",
        "ru": "✅ Меню обновлено для {}",
        "ky": "✅ {} үчүн меню жаңыртылды"
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
