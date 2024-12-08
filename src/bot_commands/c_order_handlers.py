from core_bot.core_bot import *
from bot_buttons.bot_buttons import *
from aiogram.utils.markdown import bold
from aiogram.types import CallbackQuery
import sqlite3
import datetime



##########################ORDER Lunch
async def handle_order_lunch(callback_query: types.CallbackQuery, state: FSMContext):
    current_date = datetime.datetime.now().strftime(
        date_mask)  # Get current date in YYYY-MM-DD format

    try:
        with sqlite3.connect(database_location) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT items, price FROM Lunch WHERE date = ?", (current_date,))
            rows = cursor.fetchall()

        if rows:
            # Define the maximum length for item text
            for row in rows:
                print(row[0][:MAX_TEXT_LENGTH])

            # Create dynamic lunch options
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text=f"{row[0][:MAX_TEXT_LENGTH]}..." if len(row[0]) > MAX_TEXT_LENGTH else f"{row[0]}",
                            callback_data=f"select_{row[0][:MAX_TEXT_LENGTH]}"
                        )
                    ]
                    for row in rows
                ]
            )

            # Add main menu button
            keyboard.inline_keyboard.append([InlineKeyboardButton(
                text="🔙 Main Menu", callback_data="return_main_menu")])

            await callback_query.message.edit_text(
                f"🍴 Select your lunch option for {current_date}:",
                reply_markup=keyboard
            )
            await state.set_state(OrderLunchState.selecting_lunch)
        else:
            await callback_query.message.edit_text(f"⚠️ No lunch options available for {current_date}.")

    except sqlite3.Error as e:
        await callback_query.message.edit_text(f"❌ Database error: {e}")
    await callback_query.answer()

@dp.callback_query(OrderLunchState.selecting_lunch)
async def confirm_order(callback_query: CallbackQuery, state: FSMContext):
    if callback_query.data == "return_main_menu":
        await state.clear()  # Clear the state before returning to the main menu
        await callback_query.message.edit_text("🔙 Returning to the main menu.", reply_markup=main_menu_customer_keyboard)
        return

    # Process selected lunch item
    item = callback_query.data.split("_", 1)[1]  # Extract the item name

    # Store the selected item in the state
    await state.update_data(selected_item=item)

    # Ask for confirmation
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Yes", callback_data="confirm"),
                # InlineKeyboardButton(text="✅ Specify comment and add", callback_data="confirm_with_comment"), #"confirm_with_comment"
                InlineKeyboardButton(text="❌ Cancel", callback_data="cancel"),
            ]
        ]
    )
    await callback_query.message.edit_text(
        f"Would you like to add {item} to your basket?",
        reply_markup=keyboard
    )
    await state.set_state(OrderLunchState.confirming_order)
    await callback_query.answer()

@dp.callback_query(OrderLunchState.confirming_order)
async def add_to_basket(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    item = data.get("selected_item")
    chat_id = callback_query.message.chat.id
    username = callback_query.message.chat.username
    current_date = datetime.datetime.now().strftime(date_mask)
    quantity = 1  # Default quantity for new orders

    if callback_query.data == "confirm":
        try:
            with sqlite3.connect(database_location) as conn:
                cursor = conn.cursor()

                # Fetch the price of the item from the Menu table
                cursor.execute(
                    "SELECT price FROM Lunch WHERE items like ?", (f"{item}%",))
                price_row = cursor.fetchone()

                if not price_row:
                    await callback_query.message.edit_text(f"❌ Item '{item}' not found in the menu.")
                    return

                unit_price = price_row[0]

                # Check if the item is already in the basket
                cursor.execute("""
                    SELECT ordered_quantity, total_price
                    FROM Customers_Order
                    WHERE date = ? AND chat_id = ? AND ordered_item = ?
                """, (current_date, chat_id, item))
                existing_order = cursor.fetchone()

                if existing_order:
                    # Update quantity and total price
                    existing_quantity, existing_total = existing_order
                    new_quantity = existing_quantity + quantity
                    new_total = new_quantity * unit_price

                    cursor.execute("""
                        UPDATE Customers_Order
                        SET ordered_quantity = ?, total_price = ?
                        WHERE date = ? AND chat_id = ? AND ordered_item = ?
                    """, (new_quantity, new_total, current_date, chat_id, item))
                else:
                    # Insert new row for the item
                    total_price = quantity * unit_price

                    cursor.execute("""
                        INSERT INTO Customers_Order (
                            date, chat_id, username, ordered_item,
                            ordered_quantity, unit_price, total_price
                        ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (current_date, chat_id, username, item, quantity, unit_price, total_price))

                conn.commit()

                await callback_query.message.edit_text(f"✅ {quantity}x {item} has been added to your basket.", reply_markup=main_menu_customer_keyboard)
        except sqlite3.Error as e:
            await callback_query.message.edit_text(f"❌ Database error: {e}")

    # elif callback_query.data == "confirm_with_comment":
    #     # Clear any previous state to avoid conflicts
    #     # await state.clear()

    #     # Prompt the user for a comment
    #     await callback_query.message.edit_text(f"Please type your comment for {item}:")
        
    #     # Set the state to waiting for a comment
    #     await state.set_state(OrderLunchState.waiting_for_comment)
    #     await callback_query.answer()

    elif callback_query.data == "cancel":
        await callback_query.message.edit_text("Order canceled.", reply_markup=main_menu_customer_keyboard)

    await state.clear()
    await callback_query.answer()





##################bakery
async def handle_order_bakery(callback_query: types.CallbackQuery, state: FSMContext):
    current_date = datetime.datetime.now().strftime(
        date_mask)  # Get current date in YYYY-MM-DD format

    try:
        with sqlite3.connect(database_location) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT items, price FROM Bakery WHERE date = ?", (current_date,))
            rows = cursor.fetchall()

        if rows:
            # Define the maximum length for item text
            for row in rows:
                print(row[0][:MAX_TEXT_LENGTH])

            # Create dynamic lunch options
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text=f"{row[0][:MAX_TEXT_LENGTH]}..." if len(row[0]) > MAX_TEXT_LENGTH else f"{row[0]}",
                            callback_data=f"select_{row[0][:MAX_TEXT_LENGTH]}"
                        )
                    ]
                    for row in rows
                ]
            )

            # Add main menu button
            keyboard.inline_keyboard.append([InlineKeyboardButton(
                text="🔙 Main Menu", callback_data="return_main_menu")])

            await callback_query.message.edit_text(
                f"🍴 Select your Bakery option for {current_date}:",
                reply_markup=keyboard
            )
            await state.set_state(OrderBakeryState.selecting_bakery)
        else:
            await callback_query.message.edit_text(f"⚠️ No Bakery options available for {current_date}.")

    except sqlite3.Error as e:
        await callback_query.message.edit_text(f"❌ Database error: {e}")
    await callback_query.answer()

@dp.callback_query(OrderBakeryState.selecting_bakery)
async def confirm_order(callback_query: CallbackQuery, state: FSMContext):
    if callback_query.data == "return_main_menu":
        await state.clear()  # Clear the state before returning to the main menu
        await callback_query.message.edit_text("🔙 Returning to the main menu.", reply_markup=main_menu_customer_keyboard)
        return

    # Process selected lunch item
    item = callback_query.data.split("_", 1)[1]  # Extract the item name

    # Store the selected item in the state
    await state.update_data(selected_item=item)

    # Ask for confirmation
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Yes", callback_data="confirm"),
                # InlineKeyboardButton(text="✅ Specify comment and add", callback_data="confirm_with_comment"), #"confirm_with_comment"
                InlineKeyboardButton(text="❌ Cancel", callback_data="cancel"),
            ]
        ]
    )
    await callback_query.message.edit_text(
        f"Would you like to add {item} to your basket?",
        reply_markup=keyboard
    )
    await state.set_state(OrderBakeryState.confirming_order)
    await callback_query.answer()

@dp.callback_query(OrderBakeryState.confirming_order)
async def add_to_basket(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    item = data.get("selected_item")
    chat_id = callback_query.message.chat.id
    username = callback_query.message.chat.username
    current_date = datetime.datetime.now().strftime(date_mask)
    quantity = 1  # Default quantity for new orders

    if callback_query.data == "confirm":
        try:
            with sqlite3.connect(database_location) as conn:
                cursor = conn.cursor()

                # Fetch the price of the item from the Menu table
                cursor.execute(
                    "SELECT price FROM Bakery WHERE items like ?", (f"{item}%",))
                price_row = cursor.fetchone()

                if not price_row:
                    await callback_query.message.edit_text(f"❌ Item '{item}' not found in the menu.")
                    return

                unit_price = price_row[0]

                # Check if the item is already in the basket
                cursor.execute("""
                    SELECT ordered_quantity, total_price
                    FROM Customers_Order
                    WHERE date = ? AND chat_id = ? AND ordered_item = ?
                """, (current_date, chat_id, item))
                existing_order = cursor.fetchone()

                if existing_order:
                    # Update quantity and total price
                    existing_quantity, existing_total = existing_order
                    new_quantity = existing_quantity + quantity
                    new_total = new_quantity * unit_price

                    cursor.execute("""
                        UPDATE Customers_Order
                        SET ordered_quantity = ?, total_price = ?
                        WHERE date = ? AND chat_id = ? AND ordered_item = ?
                    """, (new_quantity, new_total, current_date, chat_id, item))
                else:
                    # Insert new row for the item
                    total_price = quantity * unit_price

                    cursor.execute("""
                        INSERT INTO Customers_Order (
                            date, chat_id, username, ordered_item,
                            ordered_quantity, unit_price, total_price
                        ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (current_date, chat_id, username, item, quantity, unit_price, total_price))

                conn.commit()

                await callback_query.message.edit_text(f"✅ {quantity}x {item} has been added to your basket.", reply_markup=main_menu_customer_keyboard)
        except sqlite3.Error as e:
            await callback_query.message.edit_text(f"❌ Database error: {e}")


    elif callback_query.data == "cancel":
        await callback_query.message.edit_text("Order canceled.", reply_markup=main_menu_customer_keyboard)

    await state.clear()
    await callback_query.answer()


#################