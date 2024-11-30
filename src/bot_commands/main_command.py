from core_bot.core_bot import *
from aiogram.utils.keyboard import InlineKeyboardBuilder
from callback_data.callback_logic import *
from bot_buttons.bot_buttons import *
import re
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import sqlite3
from aiogram.utils.markdown import bold
from bot_commands.bot_handlers import *
from aiogram.fsm.context import FSMContext

hello_string = 'Hi, {}! welcome to NUR Lunch Bot! \nPlease select following options'
lier_string = "{}, you are not administrator! "

# Helper function to check admin status


def is_admin(username: str) -> bool:
    return username.lower() in ADMINS


@dp.message(CommandStart())
async def command_start_handler(message: Message, state: FSMContext) -> None:
    """
    This handler receives messages with `/start` command
    """
    # await message.answer(f"Hello, {html.bold(message.from_user.full_name)}!")
    cutomers_full_name = message.from_user.full_name
    await state.clear()
    await message.answer(hello_string.format(html.bold(cutomers_full_name)), reply_markup=start_keyboard)


CUSTOMER_ACTIONS = {
    Actions.CUSTOMER: {'handler': handle_customer, 'state': False},
    Actions.order_lunch_action: {'handler': handle_order_lunch, 'state': True},
    Actions.my_basket_action: {'handler': handle_my_basket, 'state': True},
    Actions.specify_additions_action: {'handler': handle_specify_additions, 'state': True},
    Actions.order_bakery_action: {'handler': handle_order_additional_stuff, 'state': False},
    Actions.leave_review_action: {'handler': handle_review, 'state': True},
}

ADMIN_ACTIONS = {
    Actions.administrator_action: {'handler': handle_admin, 'state': False},
    Actions.edit_lunch_menu_action: {'handler': handle_editing_lunch_menu, 'state': True},
    Actions.edit_bakekry_action: {'handler': edit_bakery_menu, 'state': True},
    Actions.current_lunch_menu_action: {'handler': handle_showing_current_lunch_menu, 'state': False},
    # Add more admin-specific actions here
    # "other_admin_action": other_admin_action,
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




# # Message handler for receiving location
# @dp.message(lambda message: message.location)
# async def handle_location(message: Message):
#     user_location = message.location
#     latitude = user_location.latitude
#     longitude = user_location.longitude

#     # Remove the keyboard after location is shared
#     await message.answer(f"We've successfully collected your location data. Thank you for sharing it! Latitude: {latitude}, Longitude: {longitude}. We'll use it to help resolve your issue", reply_markup=main_menu_customer_keyboard)
