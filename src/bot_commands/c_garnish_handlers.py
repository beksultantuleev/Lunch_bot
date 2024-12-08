from core_bot.core_bot import *
from bot_buttons.bot_buttons import *
from aiogram.utils.markdown import bold
from aiogram.types import CallbackQuery
import sqlite3
import datetime


######################Additions
'garnish'
async def handle_specify_additions(callback_query: types.CallbackQuery, state: FSMContext): 
    current_date = datetime.datetime.now().strftime(
        date_mask)  # Get current date in YYYY-MM-DD format
    chat_id = callback_query.message.chat.id
    try:
        with sqlite3.connect(database_location) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT ordered_item, ordered_quantity, additional_info FROM Customers_Order WHERE date = ? AND chat_id = ?", (current_date, chat_id))
            rows = cursor.fetchall()
            if rows:
                # keyboard = InlineKeyboardMarkup(inline_keyboard=[
                #     [
                #         InlineKeyboardButton(
                #             text=f"{qnt} x {item}", callback_data=f"select_{item}"
                #         ),
                #         InlineKeyboardButton(
                #             text="additions", callback_data=f"specify_additions_{item}"
                #         )
                #     ]
                #     for item, qnt, additions in rows
                # ])
                

                # Create dynamic lunch options
                keyboard = InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text=f"{row[1]}x{row[0][:MAX_TEXT_LENGTH]}..." if len(row[0]) > MAX_TEXT_LENGTH else f"{row[0]}",
                                callback_data=f"select_{row[0][:MAX_TEXT_LENGTH]}"
                            ),
                        #     InlineKeyboardButton(
                        #     text="additions", callback_data=f"specify_additions_{row[0][:MAX_TEXT_LENGTH]}"
                        # )
                        ]
                        for row in rows
                    ]
                )
                keyboard.inline_keyboard.append([InlineKeyboardButton(
                    text="🔙 Main Menu", callback_data="return_main_menu")])
                await callback_query.message.edit_text(
                    f"Specify additions for {current_date}:",
                    reply_markup=keyboard
                )
                await state.set_state(AdditionsState.selecting_lunch)
            else:
                await callback_query.message.edit_text(f"⚠️ your basket is empty for {current_date}.", reply_markup=main_menu_customer_keyboard)
                await callback_query.answer()
                await state.clear()
    except sqlite3.Error as e:
        await callback_query.message.edit_text(f"❌ Database error: {e}")
        await state.clear()
    await callback_query.answer()

@dp.callback_query(AdditionsState.selecting_lunch)
async def handle_addition_selection(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.data == "return_main_menu":
        await state.clear()
        await callback_query.message.edit_text(
            "🔙 Back to the main menu. Choose an option:",
            reply_markup=main_menu_customer_keyboard
        )
        return
    # elif callback_query.data.startswith("specify_additions_"):
    elif callback_query.data.startswith("select_"):
        # Extract the item name
        item_name = callback_query.data.split("select_", 1)[1]

        # Save the item in the state
        await state.update_data(selected_item=item_name)

        # Prompt the user to enter additional info
        await callback_query.message.edit_text(f"Please type the additions for {item_name}:")
        await state.set_state(AdditionsState.waiting_for_addition)
        await callback_query.answer()

async def save_additional_info(message: types.Message, state: FSMContext):
    # Get the user's input
    addition = message.text

    # Retrieve the item and other necessary data from the state
    data = await state.get_data()
    item_name = data.get("selected_item")
    chat_id = message.chat.id
    current_date = datetime.datetime.now().strftime(date_mask)

    try:
        with sqlite3.connect(database_location) as conn:
            cursor = conn.cursor()

            # Update the additional_info for the selected item
            cursor.execute("""
                UPDATE Customers_Order
                SET additional_info = ?
                WHERE date = ? AND chat_id = ? AND ordered_item = ?
            """, (addition, current_date, chat_id, item_name))
            conn.commit()

        # Notify the user
        await message.answer(f"Additional info for {item_name} has been updated. Thank you!", reply_markup=main_menu_customer_keyboard)
    except sqlite3.Error as e:
        await message.answer(f"❌ Failed to save additional info. Error: {e}", reply_markup=main_menu_customer_keyboard)

    # Clear the state after processing
    await state.clear()

dp.callback_query.register(handle_specify_additions, StateFilter(AdditionsState.selecting_lunch))
dp.callback_query.register(handle_addition_selection, StateFilter(AdditionsState.selecting_lunch))
dp.message.register(save_additional_info, StateFilter(AdditionsState.waiting_for_addition))
