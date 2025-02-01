from core_bot.core_bot import *
from bot_buttons.bot_buttons import *
from aiogram.utils.markdown import bold
from aiogram.types import CallbackQuery
import sqlite3
import datetime


# ORDER Lunch
async def handle_order_lunch(callback_query: types.CallbackQuery, state: FSMContext):
    # chat_id = message.chat.id
    chat_id = callback_query.from_user.id
    user_languages.setdefault(chat_id, default_lang)
    selected_language = user_languages.get(chat_id, default_lang)
    main_menu_customer_keyboard = create_customer_menu_buttons(chat_id, user_languages)
    current_date = datetime.datetime.now().strftime(
        date_mask)
    now = datetime.datetime.now().time()
    if now > ORDER_TIME_LIMIT:
        await callback_query.answer(f"⏳ Order time is over! You can order only before {hour_time_limit}:{min_time_limit}", show_alert=True)
        return

    try:
        with sqlite3.connect(database_location) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT items_id, items, price, available_amount FROM Lunch WHERE date = ? AND available_amount > 0 ORDER BY items", (current_date,))
            rows = cursor.fetchall()

        if rows:
            # for row in rows:
            #     print(row)
            # Define the maximum length for item text
            # row 0 is id, row 1 is item_name

            # Create dynamic lunch options
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text=f"{row[1][:MAX_TEXT_LENGTH]}..." if len(
                                row[1]) > MAX_TEXT_LENGTH else f"{row[1]}",
                            callback_data=f"select_{row[0]}"
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
            await callback_query.message.edit_text(f"⚠️ No lunch options available for {current_date}.", reply_markup=main_menu_customer_keyboard)

    except sqlite3.Error as e:
        await callback_query.message.edit_text(f"❌ Database error: {e}")
    await callback_query.answer()


@dp.callback_query(OrderLunchState.selecting_lunch)
async def confirm_order(callback_query: CallbackQuery, state: FSMContext):
    # chat_id = message.chat.id
    chat_id = callback_query.from_user.id
    user_languages.setdefault(chat_id, default_lang)
    selected_language = user_languages.get(chat_id, default_lang)
    main_menu_customer_keyboard = create_customer_menu_buttons(chat_id, user_languages)
    current_date = datetime.datetime.now().strftime(
        date_mask)
    if callback_query.data == "return_main_menu":
        await state.clear()  # Clear the state before returning to the main menu
        await callback_query.message.edit_text("🔙 Returning to the main menu.", reply_markup=main_menu_customer_keyboard)
        return

    item_id = callback_query.data.split("_", 1)[1]  # Extract the item name
    with sqlite3.connect(database_location) as conn:
        cursor = conn.cursor()

        # Fetch the price of the item from the Menu table
        cursor.execute(
            "SELECT items FROM Lunch WHERE items_id = ? and date = ?", (item_id, current_date,))
        item_name = cursor.fetchone()[0]

    # Store the selected item in the state
    await state.update_data(selected_item=item_id)

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
        f"Would you like to add '{item_name}' to your basket?",
        reply_markup=keyboard
    )
    await state.set_state(OrderLunchState.confirming_order)
    await callback_query.answer()


@dp.callback_query(OrderLunchState.confirming_order)
async def add_to_basket(callback_query: CallbackQuery, state: FSMContext):

    # chat_id = message.chat.id
    chat_id = callback_query.from_user.id
    user_languages.setdefault(chat_id, default_lang)
    selected_language = user_languages.get(chat_id, default_lang)
    main_menu_customer_keyboard = create_customer_menu_buttons(chat_id, user_languages)

    data = await state.get_data()
    item_id = data.get("selected_item")
    chat_id = callback_query.message.chat.id
    username = callback_query.message.chat.username
    current_date = datetime.datetime.now().strftime(date_mask)
    quantity = 1  # Default quantity for new orders

    if callback_query.data == "confirm":
        try:
            with sqlite3.connect(database_location) as conn:
                cursor = conn.cursor()

                # Fetch the price and available amount of the item
                cursor.execute(
                    "SELECT price, available_amount FROM Lunch WHERE items_id = ? AND date = ?", 
                    (item_id, current_date)
                )
                row = cursor.fetchone()

                if not row:
                    await callback_query.message.edit_text(f"❌ Item not found in the menu.")
                    return

                unit_price, available_amount = row

                # Fetch item name
                cursor.execute(
                    "SELECT items FROM Lunch WHERE items_id = ? AND date = ?", 
                    (item_id, current_date)
                )
                item_name = cursor.fetchone()[0]

                # Check if enough stock is available
                if available_amount < quantity:
                    await callback_query.message.edit_text(
                        f"⚠️ Not enough stock available for '{item_name}'. Only {available_amount} left.",
                        reply_markup=main_menu_customer_keyboard
                    )
                    return

                # Check if the item is already in the basket
                cursor.execute("""
                    SELECT ordered_quantity, total_price
                    FROM Customers_Order
                    WHERE date = ? AND chat_id = ? AND ordered_item = ?
                """, (current_date, chat_id, item_name))
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
                    """, (new_quantity, new_total, current_date, chat_id, item_name))
                else:
                    # Insert new row for the item
                    total_price = quantity * unit_price

                    cursor.execute("""
                        INSERT INTO Customers_Order (
                            date, chat_id, username, ordered_item_id, ordered_item,
                            ordered_quantity, unit_price, total_price
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (current_date, chat_id, username, item_id, item_name, quantity, unit_price, total_price))

                # Reduce available amount in Lunch table
                new_available_amount = available_amount - quantity
                cursor.execute("""
                    UPDATE Lunch
                    SET available_amount = ?
                    WHERE date = ? AND items_id = ?
                """, (new_available_amount, current_date, item_id))

                conn.commit()

                await callback_query.message.edit_text(
                    f"✅ {quantity}x {item_name} has been added to your basket.\n"
                    f"Remaining stock: {new_available_amount}",
                    reply_markup=main_menu_customer_keyboard
                )
        except sqlite3.Error as e:
            await callback_query.message.edit_text(f"❌ Database error: {e}")

    elif callback_query.data == "cancel":
        await callback_query.message.edit_text("❌ Order canceled.", reply_markup=main_menu_customer_keyboard)

    await state.clear()
    await callback_query.answer()


async def handle_showing_current_lunch_c_menu(callback_query: CallbackQuery):
    # chat_id = message.chat.id
    chat_id = callback_query.from_user.id
    user_languages.setdefault(chat_id, default_lang)
    selected_language = user_languages.get(chat_id, default_lang)
    main_menu_customer_keyboard = create_customer_menu_buttons(chat_id, user_languages)
    current_date = datetime.datetime.now().strftime(
        date_mask)  

    try:
        with sqlite3.connect(database_location) as conn:
            cursor = conn.cursor()
            # Use parameterized query to prevent SQL injection
            cursor.execute(
                "SELECT items, price, available_amount FROM Lunch WHERE date = ? and available_amount > 0 order by items", (current_date,))
            rows = cursor.fetchall()

        if rows:
            # Format the menu into a readable string
            menu = "\n".join(
                [f"- ({int(available_amount)}) x {item} (Price: {price})" for item, price, available_amount in rows])
                # [f"- {item} (Price: {price})" for item, price in rows])
            await callback_query.message.edit_text(f"```🍴 Today's Lunch Menu ({current_date}):\n{menu}```", reply_markup=main_menu_customer_keyboard, parse_mode="MarkdownV2")
        else:
            await callback_query.message.edit_text(f"⚠️ No lunch menu available for {current_date}.", reply_markup=main_menu_customer_keyboard)
    except sqlite3.Error as e:
        await callback_query.message.edit_text(f"❌ Database error: {e}", reply_markup=main_menu_customer_keyboard)

# # bakery
# async def handle_order_bakery(callback_query: types.CallbackQuery, state: FSMContext):
#     current_date = datetime.datetime.now().strftime(
#         date_mask)

#     try:
#         with sqlite3.connect(database_location) as conn:
#             cursor = conn.cursor()
#             cursor.execute(
#                 "SELECT items_id, items, price FROM Bakery WHERE date = ?", (current_date,))
#             rows = cursor.fetchall()

#         if rows:
#             # Create dynamic lunch options
#             keyboard = InlineKeyboardMarkup(
#                 inline_keyboard=[
#                     [
#                         InlineKeyboardButton(
#                             text=f"{row[1][:MAX_TEXT_LENGTH]}..." if len(
#                                 row[1]) > MAX_TEXT_LENGTH else f"{row[1]}",
#                             callback_data=f"select_{row[0]}"
#                         )
#                     ]
#                     for row in rows
#                 ]
#             )

#             # Add main menu button
#             keyboard.inline_keyboard.append([InlineKeyboardButton(
#                 text="🔙 Main Menu", callback_data="return_main_menu")])

#             await callback_query.message.edit_text(
#                 f"🍴 Select your lunch option for {current_date}:",
#                 reply_markup=keyboard
#             )
#             await state.set_state(OrderBakeryState.selecting_bakery)
#         else:
#             await callback_query.message.edit_text(f"⚠️ No Bakery options available for {current_date}.", reply_markup=main_menu_customer_keyboard)

#     except sqlite3.Error as e:
#         await callback_query.message.edit_text(f"❌ Database error: {e}")
#     await callback_query.answer()


# @dp.callback_query(OrderBakeryState.selecting_bakery)
# async def confirm_order(callback_query: CallbackQuery, state: FSMContext):
#     current_date = datetime.datetime.now().strftime(
#         date_mask)
#     if callback_query.data == "return_main_menu":
#         await state.clear()  # Clear the state before returning to the main menu
#         await callback_query.message.edit_text("🔙 Returning to the main menu.", reply_markup=main_menu_customer_keyboard)
#         return

#     item_id = callback_query.data.split("_", 1)[1]  # Extract the item name
#     with sqlite3.connect(database_location) as conn:
#         cursor = conn.cursor()

#         # Fetch the price of the item from the Menu table
#         cursor.execute(
#             "SELECT items FROM Bakery WHERE items_id = ? and date = ?", (item_id, current_date,))
#         item_name = cursor.fetchone()[0]

#     # Store the selected item in the state
#     await state.update_data(selected_item=item_id)

#     # Ask for confirmation
#     keyboard = InlineKeyboardMarkup(
#         inline_keyboard=[
#             [
#                 InlineKeyboardButton(text="✅ Yes", callback_data="confirm"),
#                 # InlineKeyboardButton(text="✅ Specify comment and add", callback_data="confirm_with_comment"), #"confirm_with_comment"
#                 InlineKeyboardButton(text="❌ Cancel", callback_data="cancel"),
#             ]
#         ]
#     )
#     await callback_query.message.edit_text(
#         f"Would you like to add '{item_name}' to your basket?",
#         reply_markup=keyboard
#     )
#     await state.set_state(OrderBakeryState.confirming_order)
#     await callback_query.answer()


# @dp.callback_query(OrderBakeryState.confirming_order)
# async def add_to_basket(callback_query: CallbackQuery, state: FSMContext):
#     data = await state.get_data()
#     item_id = data.get("selected_item")
#     chat_id = callback_query.message.chat.id
#     username = callback_query.message.chat.username
#     current_date = datetime.datetime.now().strftime(date_mask)
#     quantity = 1  # Default quantity for new orders

#     if callback_query.data == "confirm":
#         try:
#             with sqlite3.connect(database_location) as conn:
#                 cursor = conn.cursor()

#                 # Fetch the price of the item from the Menu table
#                 cursor.execute(
#                     "SELECT price FROM Bakery WHERE items_id = ? and date = ?", (item_id, current_date,))
#                 price_row = cursor.fetchone()

#                 cursor.execute(
#                     "SELECT items FROM Bakery WHERE items_id = ? and date = ?", (item_id, current_date,))
#                 item_name = cursor.fetchone()[0]

#                 if not price_row:
#                     await callback_query.message.edit_text(f"❌ Item '{item_name}' not found in the menu.")
#                     return

#                 unit_price = price_row[0]

#                 # Check if the item is already in the basket
#                 cursor.execute("""
#                     SELECT ordered_quantity, total_price
#                     FROM Customers_Order
#                     WHERE date = ? AND chat_id = ? AND ordered_item = ?
#                 """, (current_date, chat_id, item_name))
#                 existing_order = cursor.fetchone()

#                 if existing_order:
#                     # Update quantity and total price
#                     existing_quantity, existing_total = existing_order
#                     new_quantity = existing_quantity + quantity
#                     new_total = new_quantity * unit_price

#                     cursor.execute("""
#                         UPDATE Customers_Order
#                         SET ordered_quantity = ?, total_price = ?
#                         WHERE date = ? AND chat_id = ? AND ordered_item = ?
#                     """, (new_quantity, new_total, current_date, chat_id, item_name))
#                 else:
#                     # Insert new row for the item
#                     total_price = quantity * unit_price

#                     cursor.execute("""
#                         INSERT INTO Customers_Order (
#                             date, chat_id, username,ordered_item_id, ordered_item,
#                             ordered_quantity, unit_price, total_price
#                         ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
#                     """, (current_date, chat_id, username, item_id, item_name, quantity, unit_price, total_price))

#                 conn.commit()

#                 await callback_query.message.edit_text(f"✅ {quantity}x {item_name} has been added to your basket.", reply_markup=main_menu_customer_keyboard)
#         except sqlite3.Error as e:
#             await callback_query.message.edit_text(f"❌ Database error: {e}")

#     # elif callback_query.data == "confirm_with_comment":
#     #     # Clear any previous state to avoid conflicts
#     #     # await state.clear()

#     #     # Prompt the user for a comment
#     #     await callback_query.message.edit_text(f"Please type your comment for {item}:")

#     #     # Set the state to waiting for a comment
#     #     await state.set_state(OrderLunchState.waiting_for_comment)
#     #     await callback_query.answer()

#     elif callback_query.data == "cancel":
#         await callback_query.message.edit_text("Order canceled.", reply_markup=main_menu_customer_keyboard)

#     await state.clear()
#     await callback_query.answer()


#################
