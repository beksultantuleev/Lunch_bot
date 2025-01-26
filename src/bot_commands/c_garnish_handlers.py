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
                "SELECT ordered_item_id, ordered_item, ordered_quantity, additional_info FROM Customers_Order WHERE date = ? AND chat_id = ?", (current_date, chat_id))
            rows = cursor.fetchall()
            if rows:
              

                # Create dynamic lunch options
                keyboard = InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text=f"{row[1][:MAX_TEXT_LENGTH]}..." if len(row[1]) > MAX_TEXT_LENGTH else f"{row[1]}",
                                callback_data=f"select_{row[0]}"
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
    current_date = datetime.datetime.now().strftime(
        date_mask)
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
        item_id = callback_query.data.split("select_", 1)[1]

        # Save the item in the state
        await state.update_data(selected_item=item_id)
        with sqlite3.connect(database_location) as conn:
            cursor = conn.cursor()
            print(f'this is item ID: {item_id}')

            # Fetch the price of the item from the Menu table
            cursor.execute(
                """
                SELECT items FROM Lunch WHERE items_id = ? and date = ?
                UNION ALL 
                SELECT items FROM Bakery WHERE items_id = ? and date = ?
                """, (item_id, current_date, item_id, current_date,)  # Pass item_id twice
            )

            item_name = cursor.fetchone()[0]
            # else:
            #     cursor.execute(
            #         "SELECT items FROM Bakery WHERE items_id = ?", (item_id,))
            #     item_name = cursor.fetchone()[0]
            print(f'item_name is {item_name}')


        # Prompt the user to enter additional info
        await callback_query.message.edit_text(f"Please type the additions for {item_name}:")
        await state.set_state(AdditionsState.waiting_for_addition)
        await callback_query.answer()

async def save_additional_info(message: types.Message, state: FSMContext):
    current_date = datetime.datetime.now().strftime(
        date_mask)
    # Get the user's input
    addition = message.text

    # Retrieve the item and other necessary data from the state
    data = await state.get_data()
    item_id = data.get("selected_item")
    chat_id = message.chat.id
    current_date = datetime.datetime.now().strftime(date_mask)

    try:
        with sqlite3.connect(database_location) as conn:
            cursor = conn.cursor()
            
            cursor.execute(
                """
                SELECT items FROM Lunch WHERE items_id = ? and date = ?
                UNION ALL 
                SELECT items FROM Bakery WHERE items_id = ? and date = ?
                """, (item_id, current_date, item_id, current_date,)  # Pass item_id twice
            )

            item_name = cursor.fetchone()[0]

            # Update the additional_info for the selected item
            cursor.execute("""
                UPDATE Customers_Order
                SET additional_info = ?
                WHERE date = ? AND chat_id = ? AND ordered_item_id = ?
            """, (addition, current_date, chat_id, item_id))
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
