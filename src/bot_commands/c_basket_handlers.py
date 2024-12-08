from core_bot.core_bot import *
from bot_buttons.bot_buttons import *
from aiogram.utils.markdown import bold
from aiogram.types import CallbackQuery
import sqlite3
import datetime



############################BASKET

async def handle_my_basket(callback_query: types.CallbackQuery, state: FSMContext): 
    current_date = datetime.datetime.now().strftime(
        date_mask)  # Get current date in YYYY-MM-DD format
    chat_id = callback_query.message.chat.id
    unpaid_total_price = 0
    total_price = 0

    try:
        with sqlite3.connect(database_location) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT ordered_item, ordered_quantity, total_price FROM Customers_Order WHERE date = ? AND chat_id = ?", (current_date, chat_id))
            rows = cursor.fetchall()

            'previous unpaid orders'
            cursor.execute(
                "SELECT ordered_item, ordered_quantity, total_price FROM Customers_Order WHERE date != ? AND chat_id = ? and is_paid = 0", (current_date, chat_id))
            unpaid_rows = cursor.fetchall()

            if unpaid_rows:
                for row in unpaid_rows:
                    unpaid_total_price += row[2]
                print(f'this is total unpaid price: {unpaid_total_price}')

            if rows:

                for row in rows:
                    total_price += row[2]
                    print(row)
                print(f'this is total price: {total_price}')
                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text=f"{qnt} x {item} - {price} KGS", callback_data=f"select_{item}"
                        ),
                        InlineKeyboardButton(
                            text="❌", callback_data=f"delete_{item}"
                        )
                    ]
                    for item, qnt, price in rows
                ])
                keyboard.inline_keyboard.append([InlineKeyboardButton(
                    text=f"Debt: {unpaid_total_price} KGS", callback_data="noop")])
                keyboard.inline_keyboard.append([InlineKeyboardButton(
                    text=f"Total: {total_price + unpaid_total_price} KGS", callback_data="noop")])
                keyboard.inline_keyboard.append([InlineKeyboardButton(
                    text="🔙 Main Menu", callback_data="return_main_menu")])
                await callback_query.message.edit_text(
                    f"🍴 you basket for {current_date}:",
                    reply_markup=keyboard
                )
                await state.set_state(BasketState.viewing_basket)
            else:
                await callback_query.message.edit_text(f"⚠️ your basket is empty for {current_date}.", reply_markup=main_menu_customer_keyboard)
                await callback_query.answer()
                await state.clear()

                
    except sqlite3.Error as e:
        await callback_query.message.edit_text(f"❌ Database error: {e}")
        await state.clear()
    await callback_query.answer()


@dp.callback_query(BasketState.viewing_basket)
async def update_basket(callback_query: CallbackQuery, state: FSMContext):
    data = callback_query.data
    # user_data = await state.get_data()
    current_date = datetime.datetime.now().strftime(
        date_mask)  # Get current date in YYYY-MM-DD format
    chat_id = callback_query.message.chat.id

    if data == "return_main_menu":
        await state.clear()
        await callback_query.message.edit_text(
            "🔙 Back to the main menu. Choose an option:",
            reply_markup=main_menu_customer_keyboard
        )
        return
    
    if data.startswith("delete_"):
        item_name = data.split("_", 1)[1]
        print(f'this is item name: {item_name}\nchat_Id: {chat_id}\ndate: {current_date}')

        try:
            with sqlite3.connect(database_location) as conn:
                cursor = conn.cursor()

                # Delete the item from the basket
                cursor.execute("""
                    DELETE FROM Customers_Order
                    WHERE date = ? AND chat_id = ? AND ordered_item = ?
                """, (current_date, chat_id, item_name))

                conn.commit()
            await callback_query.answer("Item deleted from basket.")
            # Refresh the basket view
            await handle_my_basket(callback_query, state)


        except sqlite3.Error as e:
            await callback_query.message.edit_text(f"❌ Database error: {e}")
            await state.clear()

    # await callback_query.answer()
    # await state.clear()

############################



