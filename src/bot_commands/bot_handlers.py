from core_bot.core_bot import *
from bot_buttons.bot_buttons import *
from aiogram.utils.markdown import bold
from aiogram.types import CallbackQuery
# from aiogram.dispatcher.filters import CallbackData

###Customer handlers
# Handler functions
async def handle_customer(callback_query: types.CallbackQuery):
    await callback_query.message.edit_text(
        "Select your actions:", reply_markup=main_menu_customer_keyboard
    )

async def handle_order_lunch(callback_query: types.CallbackQuery):
    await callback_query.message.answer(
        "Select your lunch options:",
        reply_markup=location_keyboard,
    )

async def handle_order_additional_stuff(callback_query: types.CallbackQuery):
    await callback_query.message.edit_text("You selected voice_action!")



async def handle_non_admin_access(callback_query: types.CallbackQuery, full_name: str):
    lier_string = "Sorry {}, you are not an admin!".format(bold(full_name))
    await callback_query.message.edit_text(
        lier_string, reply_markup=main_menu_customer_keyboard
    )

async def return_to_main_menu(callback_query: types.CallbackQuery, full_name: str):
    hello_string = "Welcome back, {}!".format(bold(full_name))
    await callback_query.message.edit_text(
        hello_string, reply_markup=start_keyboard
    )

#############Admin handlers

async def handle_admin(callback_query: types.CallbackQuery):
    await callback_query.message.edit_text(
        "Your Admin options:", reply_markup=main_menu_admin_keyboard
    )

# Admin action handlers
async def edit_lunch_menu(callback_query: CallbackQuery):
    await callback_query.message.edit_text(
        "Editing lunch menu options... (Admin feature)",
        reply_markup=main_menu_admin_keyboard,
    )

async def edit_bakery_menu(callback_query: CallbackQuery):
    await callback_query.message.edit_text(
        "Editing bakery menu options... (Admin feature)",
        reply_markup=main_menu_admin_keyboard,
    )

async def other_admin_action(callback_query: CallbackQuery):
    await callback_query.message.edit_text(
        "Performing another admin action!",
        reply_markup=main_menu_admin_keyboard,
    )