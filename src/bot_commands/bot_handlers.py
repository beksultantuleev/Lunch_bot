from core_bot.core_bot import *
from bot_buttons.bot_buttons import *
from aiogram.utils.markdown import bold
from aiogram.types import CallbackQuery
import sqlite3
import datetime

# from aiogram.dispatcher.filters import CallbackData

# Customer handlers


async def handle_customer(callback_query: types.CallbackQuery):
    # chat_id = message.chat.id
    chat_id = callback_query.from_user.id
    user_languages.setdefault(chat_id, default_lang)
    selected_language = user_languages.get(chat_id, default_lang)
    main_menu_customer_keyboard = create_customer_menu_buttons(
        chat_id, user_languages)
    customer_menu_options_str = get_translation(
        "customer_menu_options_str", selected_language)
    await callback_query.message.edit_text(
        customer_menu_options_str, reply_markup=main_menu_customer_keyboard
    )

###########################


async def handle_non_admin_access(callback_query: types.CallbackQuery, full_name: str):
    # chat_id = message.chat.id
    chat_id = callback_query.from_user.id
    user_languages.setdefault(chat_id, default_lang)
    selected_language = user_languages.get(chat_id, default_lang)
    main_menu_customer_keyboard = create_customer_menu_buttons(
        chat_id, user_languages)
    lier_string = get_translation("lier_string", selected_language)

    lier_string = lier_string.format(bold(full_name))
    await callback_query.message.edit_text(
        lier_string, reply_markup=main_menu_customer_keyboard
    )


async def return_to_main_menu(callback_query: types.CallbackQuery, full_name: str):

    chat_id = callback_query.from_user.id
    user_languages.setdefault(chat_id, default_lang)
    selected_language = user_languages.get(chat_id, default_lang)
    hello_string = get_translation("hello_string", selected_language)

    start_keyboard = create_initial_buttons(chat_id, user_languages)

    await callback_query.message.edit_text(
        hello_string.format(full_name), reply_markup=start_keyboard
    )

# Admin handlers


async def handle_admin(callback_query: types.CallbackQuery):
    chat_id = callback_query.from_user.id
    user_languages.setdefault(chat_id, default_lang)
    selected_language = user_languages.get(chat_id, default_lang)
    customer_menu_options_str = get_translation("customer_menu_options_str", selected_language)

    main_menu_admin_keyboard = create_admin_menu_buttons(
        chat_id, user_languages)
    await callback_query.message.edit_text(
        customer_menu_options_str, reply_markup=main_menu_admin_keyboard
    )


######

# async def other_admin_action(callback_query: CallbackQuery):
#     # chat_id = message.chat.id
#     chat_id = callback_query.from_user.id
#     user_languages.setdefault(chat_id, default_lang)
#     selected_language = user_languages.get(chat_id, default_lang)
#     main_menu_admin_keyboard = create_admin_menu_buttons(
#         chat_id, user_languages)
#     await callback_query.message.edit_text(
#         "Performing another admin action!",
#         reply_markup=main_menu_admin_keyboard,
#     )
