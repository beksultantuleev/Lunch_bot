from core_bot.core_bot import *
from bot_buttons.bot_buttons import *
from aiogram.utils.markdown import bold
from aiogram.types import CallbackQuery
import sqlite3
import datetime

# from aiogram.dispatcher.filters import CallbackData

# Customer handlers
# Handler functions


async def handle_customer(callback_query: types.CallbackQuery):
    await callback_query.message.edit_text(
        "Select your actions:", reply_markup=main_menu_customer_keyboard
    )


async def handle_order_lunch(callback_query: types.CallbackQuery, state: FSMContext):
    current_date = datetime.datetime.now().strftime(
        "%d-%m-%Y")  # Get current date in YYYY-MM-DD format

    try:
        with sqlite3.connect(database_location) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT items, price FROM Lunch WHERE date = ?", (current_date,))
            rows = cursor.fetchall()

        if rows:
            # Create dynamic lunch options
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text=f"{item} - {price} KGS", callback_data=f"select_{item}")]
                    for item, price in rows
                ]
            )

            # Add main menu button
            keyboard.inline_keyboard.append([InlineKeyboardButton(text="🔙 Main Menu", callback_data="return_main_menu")])

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
    # await callback_query.message.answer(
    #     "Select your lunch options:",
    #     reply_markup=location_keyboard,
    # )

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

                # Fetch the price of the selected lunch item
                cursor.execute("SELECT price FROM Lunch WHERE items = ?", (item,))
                lunch_price_row = cursor.fetchone()

                if lunch_price_row:
                    lunch_price = lunch_price_row[0]
                    total_price = lunch_price * quantity

                    # Check if an order for this user and date already exists
                    cursor.execute("""
                        SELECT lunch_quantity, price_lunch, price_total
                        FROM Customers_Order
                        WHERE date = ? AND chat_id = ?
                    """, (current_date, chat_id))
                    existing_order = cursor.fetchone()

                    if existing_order:
                        # Update the existing order
                        existing_quantity = existing_order[0]
                        existing_price_lunch = existing_order[1]
                        existing_total_price = existing_order[2]

                        new_quantity = existing_quantity + quantity
                        new_price_lunch = existing_price_lunch + total_price
                        new_total_price = existing_total_price + total_price

                        cursor.execute("""
                            UPDATE Customers_Order
                            SET lunch_quantity = ?, price_lunch = ?, price_total = ?
                            WHERE date = ? AND chat_id = ?
                        """, (new_quantity, new_price_lunch, new_total_price, current_date, chat_id))
                    else:
                        # Insert a new order
                        cursor.execute("""
                            INSERT INTO Customers_Order (
                                date, chat_id, username, lunch_item, lunch_quantity,
                                bakery_item, bakery_quantity, price_lunch, price_bakery, price_total
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (current_date, chat_id, username, item, quantity, None, 0, lunch_price, 0, total_price))

                    conn.commit()
                    await callback_query.message.edit_text(f"✅ {quantity}x {item} has been added to your basket.", reply_markup=main_menu_customer_keyboard)
                else:
                    await callback_query.message.edit_text(f"❌ Failed to add {item} to your basket. Item not found.", reply_markup=main_menu_customer_keyboard)

        except sqlite3.Error as e:
            await callback_query.message.edit_text(f"❌ Database error: {e}", reply_markup=main_menu_customer_keyboard)

    elif callback_query.data == "cancel":
        await callback_query.message.edit_text("Order canceled.", reply_markup=main_menu_customer_keyboard)

    await state.clear()
    await callback_query.answer()



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

# Admin handlers


async def handle_admin(callback_query: types.CallbackQuery):
    await callback_query.message.edit_text(
        "Your Admin options:", reply_markup=main_menu_admin_keyboard
    )

# Admin action handlers


async def handle_editing_lunch_menu(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.answer(
        "Please send the lunch menu details in the format:\n"
        "Manty"
        "Pasta",
        parse_mode="Markdown",
    )
    await state.set_state(EditLunchMenuState.waiting_for_menu_text)
    # await callback_query.message.edit_text(
    #     "Editing lunch menu options... (Admin feature)",
    #     reply_markup=main_menu_admin_keyboard,
    # )


@dp.message(EditLunchMenuState.waiting_for_menu_text)
async def process_lunch_menu_input(message: types.Message, state: FSMContext):
    input_text = message.text.strip()
    current_date = datetime.datetime.now().strftime("%d-%m-%Y")  # Get current date
    menu_items = input_text.split("\n")
    # conn = sqlite3.connect(database_location)
    # cursor = conn.cursor()
    with sqlite3.connect(database_location) as conn:
        cursor = conn.cursor()
        try:
            # Insert each menu item into the database
            for item in menu_items:
                item = item.strip()  # Clean up whitespace
                if not item:
                    continue  # Skip empty lines

                # Insert into the database
                cursor.execute(
                    "INSERT INTO Lunch (date, items, price) VALUES (?, ?, ?)",
                    (current_date, item, FIXED_PRICE),
                )

            conn.commit()  # Commit all changes at once

            await message.answer(f"✅ Menu added for {current_date}:\n" + "\n".join(f"- {item}" for item in menu_items), reply_markup=main_menu_admin_keyboard)
        except sqlite3.IntegrityError as e:
            await message.answer("❌ Some items already exist in the database.")
        except Exception as e:
            await message.answer(f"❌ An error occurred: {str(e)}")
        finally:
            await state.clear()


async def handle_showing_current_lunch_menu(callback_query: CallbackQuery):
    current_date = datetime.datetime.now().strftime(
        "%d-%m-%Y")  # Get current date in YYYY-MM-DD format

    try:
        with sqlite3.connect(database_location) as conn:
            cursor = conn.cursor()
            # Use parameterized query to prevent SQL injection
            cursor.execute(
                "SELECT items, price FROM Lunch WHERE date = ?", (current_date,))
            rows = cursor.fetchall()

        if rows:
            # Format the menu into a readable string
            menu = "\n".join(
                [f"- {item} (Price: {price})" for item, price in rows])
            await callback_query.message.answer(f"🍴 Today's Lunch Menu ({current_date}):\n{menu}")
        else:
            await callback_query.message.answer(f"⚠️ No lunch menu available for {current_date}.")
    except sqlite3.Error as e:
        await callback_query.message.answer(f"❌ Database error: {e}")
    # await callback_query.message.edit_text(
    #     "Performing another admin action!",
    #     reply_markup=main_menu_admin_keyboard,
    # )


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
