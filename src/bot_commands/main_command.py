from core_bot.core_bot import *
from aiogram.utils.keyboard import InlineKeyboardBuilder
from callback_data.callback_logic import *
from bot_buttons.bot_buttons import *
import re
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import sqlite3
from aiogram.utils.markdown import bold
from bot_commands.bot_handlers import *
from bot_commands.c_order_handlers import *
from bot_commands.c_garnish_handlers import *
from bot_commands.c_basket_handlers import *
from bot_commands.c_review_handlers import *
from bot_commands.c_raiting_handlers import *
from bot_commands.a_menu_handlers import *
from aiogram.fsm.context import FSMContext
from aiogram import Router, F



# Helper function to check admin status


def is_admin(username: str) -> bool:
    return username.lower() in ADMINS


@dp.message(CommandStart())
async def command_start_handler(message: Message, state: FSMContext) -> None:
    """
    This handler receives messages with `/start` command
    """

    # await message.answer(f"Hello, {html.bold(message.from_user.full_name)}!")
    chat_id = message.chat.id
    user_languages.setdefault(chat_id, default_lang)
    selected_language = user_languages.get(chat_id, default_lang)
    
    hello_string = get_translation("hello_string", selected_language)
    # lier_string = get_translation("lier_string", selected_language)
    start_keyboard = create_initial_buttons(chat_id, user_languages)
    cutomers_full_name = message.from_user.full_name
    await state.clear()
    await message.answer(hello_string.format(html.bold(cutomers_full_name)), reply_markup=start_keyboard)


@dp.message(Command("cancel"))
async def command_cancel_handler(message: Message, state: FSMContext) -> None:
    """
    This handler receives messages with `/cancel` command
    """
    chat_id = message.chat.id
    user_languages.setdefault(chat_id, default_lang)
    selected_language = user_languages.get(chat_id, default_lang)
    start_keyboard = create_initial_buttons(chat_id, user_languages)

    current_state = await state.get_state()
    if current_state is None:
        await message.answer("You are not in any active state.")
    else:
        await state.clear()  # Clear all FSM states and data
        await message.answer(
            "All states have been canceled. If you need further assistance, you can start again with /start.",
            reply_markup=start_keyboard,
        )



CUSTOMER_ACTIONS = {
    Actions.CUSTOMER: {'handler': handle_customer, 'state': False},
    Actions.order_lunch_action: {'handler': handle_order_lunch, 'state': True},
    Actions.my_basket_action: {'handler': handle_my_basket, 'state': True},
    Actions.specify_additions_action: {'handler': handle_specify_additions, 'state': True},
    # Actions.order_bakery_action: {'handler': handle_order_bakery, 'state': True},
    Actions.leave_review_action: {'handler': handle_review, 'state': True},
    Actions.rate_your_lunch_action: {'handler': handle_rating, 'state': True},
    Actions.lunch_rating_list_action: {'handler': handle_showing_rating_menu, 'state': False},
    Actions.current_lunch_menu_c_action: {'handler': handle_showing_current_lunch_c_menu, 'state': False},
    Actions.export_review_wc_action: {'handler': handle_word_cloud_review, 'state': False},
}

ADMIN_ACTIONS = {
    Actions.administrator_action: {'handler': handle_admin, 'state': False},
    Actions.edit_lunch_menu_action: {'handler': handle_editing_lunch_menu, 'state': True},
    # Actions.edit_bakekry_action: {'handler': handle_editing_bakery_menu, 'state': True},
    Actions.current_lunch_menu_action: {'handler': handle_showing_current_lunch_menu, 'state': False},
    Actions.export_today_excel_action: {'handler': handle_today_export_orders, 'state': False},
    Actions.export_all_excel_action: {'handler': handle_all_export_orders, 'state': False},
    Actions.export_review_excel_action: {'handler': handle_review_export, 'state': False},
    # Actions.current_bakekry_action: {'handler': handle_showing_current_bakery_menu, 'state': False},
}


# Register message handler
# dp.message.register(save_comment, StateFilter(OrderLunchState.waiting_for_comment))

@dp.callback_query(StartCallbackData.filter())
async def start_callback_handler(callback_query: types.CallbackQuery, callback_data: StartCallbackData, state: FSMContext):
    username = callback_query.message.chat.username
    full_name = callback_query.message.chat.full_name

    action = callback_data.action

    if action in CUSTOMER_ACTIONS:  # Check if it's a customer action
        if CUSTOMER_ACTIONS[action]['state']:
            await CUSTOMER_ACTIONS[action]['handler'](callback_query, state)
        else:
            await CUSTOMER_ACTIONS[action]['handler'](callback_query)

    elif action in ADMIN_ACTIONS:  # Check if it's an admin action
        if is_admin(username):
            if ADMIN_ACTIONS[action]['state']:
                await ADMIN_ACTIONS[action]['handler'](callback_query, state)
            else:
                await ADMIN_ACTIONS[action]['handler'](callback_query)

        else:
            await handle_non_admin_access(callback_query, full_name)

    elif action == Actions.return_main_menu_action:
        await return_to_main_menu(callback_query, full_name)

    await callback_query.answer()  # Acknowledge the callback query


@dp.message(Command("en"))
async def set_language_en(message: Message):
    chat_id = message.chat.id
    user_languages[chat_id] = "en"  # Set language to English
    keyboard = create_initial_buttons(chat_id, user_languages)

    await message.reply("Language set to English!", reply_markup=keyboard)


@dp.message(Command("ru"))
async def set_language_ru(message: Message):
    chat_id = message.chat.id
    user_languages[chat_id] = "ru"  # Set language to Russian
    keyboard = create_initial_buttons(chat_id, user_languages)
    await message.reply("Язык установлен на русский!", reply_markup=keyboard)


@dp.message(Command("ky"))
async def set_language_ky(message: Message):
    chat_id = message.chat.id
    user_languages[chat_id] = "ky"  # Set language to Kyrgyz
    keyboard = create_initial_buttons(chat_id, user_languages)
    await message.reply("Тил кыргыз тилине коюлду!", reply_markup=keyboard)
