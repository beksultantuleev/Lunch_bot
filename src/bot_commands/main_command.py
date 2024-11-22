from core_bot.core_bot import *
from aiogram.utils.keyboard import InlineKeyboardBuilder
from callback_data.callback_logic import *
from bot_buttons.bot_buttons import *
import re
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import sqlite3
from aiogram.utils.markdown import bold
from bot_commands.bot_handlers import *

hello_string = 'Hi, {}! welcome to NUR Lunch Bot! \nPlease select following options'
lier_string = "{}, you are not administrator! "

# Helper function to check admin status
def is_admin(username: str) -> bool:
    return username.lower() in ADMINS


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    # await message.answer(f"Hello, {html.bold(message.from_user.full_name)}!")
    cutomers_full_name = message.from_user.full_name
    await message.answer(hello_string.format(html.bold(cutomers_full_name)), reply_markup=start_keyboard)

CUSTOMER_ACTIONS = {
    Actions.CUSTOMER: handle_customer,
    Actions.order_lunch_action: handle_order_lunch,
    Actions.order_additional_stuff_action: handle_order_additional_stuff,
    # Add more admin-specific actions here
    # "other_admin_action": other_admin_action,
}

ADMIN_ACTIONS = {
    Actions.administrator_action: handle_admin,
    Actions.edit_lunch_menu_action: edit_lunch_menu,
    Actions.edit_bakekry_action: edit_bakery_menu,
    # Add more admin-specific actions here
    # "other_admin_action": other_admin_action,
}


@dp.callback_query(StartCallbackData.filter())
async def start_callback_handler(callback_query: types.CallbackQuery, callback_data: StartCallbackData):
    username = callback_query.message.chat.username
    full_name = callback_query.message.chat.full_name

    action = callback_data.action

    if action in CUSTOMER_ACTIONS:  # Check if it's a customer action
        await CUSTOMER_ACTIONS[action](callback_query)


    elif action in ADMIN_ACTIONS:  # Check if it's an admin action
        if is_admin(username):
            await ADMIN_ACTIONS[action](callback_query)
        else:
            await handle_non_admin_access(callback_query, full_name)

    elif action == Actions.return_main_menu_action:
        await return_to_main_menu(callback_query, full_name)

    await callback_query.answer()  # Acknowledge the callback query





# Message handler for receiving location
@dp.message(lambda message: message.location)
async def handle_location(message: Message):
    user_location = message.location
    latitude = user_location.latitude
    longitude = user_location.longitude

    # Remove the keyboard after location is shared
    await message.answer(f"We've successfully collected your location data. Thank you for sharing it! Latitude: {latitude}, Longitude: {longitude}. We'll use it to help resolve your issue", reply_markup=main_menu_customer_keyboard)



