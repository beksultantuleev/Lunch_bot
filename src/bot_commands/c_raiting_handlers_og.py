from core_bot.core_bot import *
from bot_buttons.bot_buttons import *
from aiogram.utils.markdown import bold
from aiogram.types import CallbackQuery
import sqlite3
import datetime

'not in use'

############################raiting
async def handle_rating(callback_query: types.CallbackQuery, state: FSMContext): 
    current_date = datetime.datetime.now().strftime(
        date_mask)  
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
                    f"Rate your lunch for {current_date}:",
                    reply_markup=keyboard
                )
                await state.set_state(RaitingState.selecting_lunch)
            else:
                await callback_query.message.edit_text(f"⚠️ your basket is empty for {current_date}.", reply_markup=main_menu_customer_keyboard)
                await callback_query.answer()
                await state.clear()
    except sqlite3.Error as e:
        await callback_query.message.edit_text(f"❌ Database error: {e}")
        await state.clear()
    await callback_query.answer()

@dp.callback_query(RaitingState.selecting_lunch)
async def handle_rating_selection(callback_query: types.CallbackQuery, state: FSMContext):
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

            cursor.execute(
                """
                SELECT items FROM Lunch WHERE items_id = ? and date = ?
                UNION ALL 
                SELECT items FROM Bakery WHERE items_id = ? and date = ?
                """, (item_id, current_date, item_id, current_date,)  # Pass item_id twice
            )

            item_name = cursor.fetchone()[0]

            print(f'item_name is {item_name}')

        rate_excellent_btn = InlineKeyboardButton(
            text="Awesome", callback_data='rate_awesome')

        rate_good_btn = InlineKeyboardButton(
            text="Good", callback_data='rate_good')
        rate_bad_btn = InlineKeyboardButton(
            text="Bad", callback_data='rate_bad')

        rate_keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [rate_bad_btn, rate_good_btn, rate_excellent_btn],
        ])
        rate_keyboard.inline_keyboard.append([InlineKeyboardButton(
            text="🔙 Main Menu", callback_data="return_main_menu")])

        # Prompt the user to enter additional info
        await callback_query.message.edit_text(f"Please rate {item_name}:", reply_markup=rate_keyboard)
        await state.set_state(RaitingState.set_raiting)
        await callback_query.answer()

@dp.callback_query(RaitingState.set_raiting)
async def handle_raiting_set(callback_query: types.CallbackQuery, state: FSMContext):
    print(f'in rating handler')
    chat_id = callback_query.message.chat.id
    data = callback_query.data
    if data == "return_main_menu":
        await state.clear()
        await callback_query.message.edit_text(
            "🔙 Back to the main menu. Choose an option:",
            reply_markup=main_menu_customer_keyboard
        )
        return
    rating_score = None
    if data == 'rate_awesome':
        rating_score = 5
    elif data == 'rate_good':
        rating_score = 3
    elif data == 'rate_bad':
        rating_score = 1
    if rating_score:
        try:
            with sqlite3.connect(database_location) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE Customers_Order
                    SET is_paid = 1,
                        payment_type = 'cash'
                    WHERE chat_id = ? AND is_paid = 0
                """, (chat_id,))
                conn.commit()

            await callback_query.message.edit_text("✅ Payment completed with cash. Thank you!", reply_markup=main_menu_customer_keyboard)
            await state.clear()

        except sqlite3.Error as e:
            await callback_query.message.edit_text(f"❌ Database error: {e}")
            await state.clear()

############################