from core_bot.core_bot import *
from aiogram.utils.keyboard import InlineKeyboardBuilder
from callback_data.callback_logic import *
from bot_buttons.bot_buttons import *
import re
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import sqlite3

hello_string = 'Hi, {}! welcome to NUR Lunch Bot! \nPlease select following options'
lier_string = "{}, you are not administrator! "



@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    # await message.answer(f"Hello, {html.bold(message.from_user.full_name)}!")
    cutomers_full_name = message.from_user.full_name
    await message.answer(hello_string.format(html.bold(cutomers_full_name)), reply_markup=start_keyboard)


@dp.callback_query(StartCallbackData.filter())
async def start_callback_handler(callback_query: types.CallbackQuery, callback_data: StartCallbackData):
    cutomers_full_name = callback_query.message.chat.full_name
    cutomers_username = callback_query.message.chat.username
    # print(f'top callback data action is: {callback_data.action}')
    # print(f'this is callback query data: {callback_query.message}')
    # print(f'this is username: {callback_query.message.chat.username}')
    if callback_data.action == customer_action:
        await callback_query.message.edit_text("Select you issue:", reply_markup=main_menu_customer_keyboard)

    elif callback_data.action == order_lunch_action:
        # Create a keyboard to request location
        await callback_query.message.answer("Please share your location to help resolve the internet issue:", reply_markup=location_keyboard)

    elif callback_data.action == order_additional_stuff_action:
        await callback_query.message.edit_text("You selected voice_action!")

    elif callback_data.action == administrator_action:
        if cutomers_username.lower().startswith('kazama'):
            # if callback_query.message.from_user.language_code
            await callback_query.message.edit_text("Upload Screenshot for you application:", reply_markup=main_menu_commissioner_keyboard)
        else:
            await callback_query.message.edit_text(lier_string.format(html.bold(cutomers_full_name)), reply_markup=main_menu_customer_keyboard)

    elif callback_data.action == return_main_menu_action:
        await callback_query.message.edit_text(hello_string.format(html.bold(cutomers_full_name)), reply_markup=start_keyboard)

    await callback_query.answer()  # Acknowledge the callback query


# Message handler for receiving location
@dp.message(lambda message: message.location)
async def handle_location(message: Message):
    user_location = message.location
    latitude = user_location.latitude
    longitude = user_location.longitude

    # Remove the keyboard after location is shared
    await message.answer(f"We've successfully collected your location data. Thank you for sharing it! Latitude: {latitude}, Longitude: {longitude}. We'll use it to help resolve your issue", reply_markup=main_menu_customer_keyboard)



