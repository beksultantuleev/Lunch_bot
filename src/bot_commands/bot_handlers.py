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

##########################ORDER
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
            # Create dynamic lunch options
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(
                        text=f"{item} - {price} KGS", callback_data=f"select_{item}")]
                    for item, price in rows
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
                    "SELECT price FROM Lunch WHERE items = ?", (item,))
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


# async def save_comment(message: Message, state: FSMContext):
    # Not working
#     print('in comment')
#     review = message.text
#     print(f'this is review: {review}')
#     chat_id = message.chat.id
#     username = message.chat.username
#     await state.clear()

# # Register the handlers explicitly
# dp.callback_query.register(add_to_basket, StateFilter(OrderLunchState.confirming_order))
# dp.message.register(save_comment, StateFilter(OrderLunchState.waiting_for_comment))

############################


######################Additions
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
                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text=f"{qnt} x {item}", callback_data=f"select_{item}"
                        ),
                        InlineKeyboardButton(
                            text="additions", callback_data=f"specify_additions_{item}"
                        )
                    ]
                    for item, qnt, additions in rows
                ])
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
    elif callback_query.data.startswith("specify_additions_"):
        # Extract the item name
        item_name = callback_query.data.split("specify_additions_", 1)[1]

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


###########################

############################BASKET

async def handle_my_basket(callback_query: types.CallbackQuery, state: FSMContext): 
    current_date = datetime.datetime.now().strftime(
        date_mask)  # Get current date in YYYY-MM-DD format
    chat_id = callback_query.message.chat.id
    try:
        with sqlite3.connect(database_location) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT ordered_item, ordered_quantity, total_price FROM Customers_Order WHERE date = ? AND chat_id = ?", (current_date, chat_id))
            rows = cursor.fetchall()
            if rows:

                # for row in rows:
                #     print(row)
                # Create dynamic lunch options
                # keyboard = InlineKeyboardMarkup(
                #     inline_keyboard=[
                #         [InlineKeyboardButton(
                #             text=f"{qnt} x {item} - {price} KGS", callback_data=f"select_{item}")]
                #         for item, qnt, price in rows
                #     ]
                # )
                total_price = 0
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
                    text=f"Total: {total_price} KGS", callback_data="noop")])
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


############################Comment
async def handle_review(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.edit_text("Please type your review:")
    
    # Set state to waiting for the review
    await state.set_state(ReviewState.waiting_for_review)
    await callback_query.answer()


async def save_review(message: Message, state: FSMContext):
    current_date = datetime.datetime.now().strftime(date_mask)  # Current date in YYYY-MM-DD format
    review = message.text
    chat_id = message.chat.id
    username = message.chat.username

    try:
        # Insert or append the review into the database
        with sqlite3.connect(database_location) as conn:
            cursor = conn.cursor()
            
            # Check if a review already exists for this date and chat_id
            cursor.execute("""
                SELECT review FROM Customers_Review WHERE date = ? AND chat_id = ?
            """, (current_date, chat_id))
            existing_review = cursor.fetchone()

            if existing_review:
                # Append the new review to the existing one
                updated_review = existing_review[0] + ". " + review
                cursor.execute("""
                    UPDATE Customers_Review
                    SET review = ?
                    WHERE date = ? AND chat_id = ?
                """, (updated_review, current_date, chat_id))
            else:
                # Insert a new review
                cursor.execute("""
                    INSERT INTO Customers_Review (date, chat_id, username, review)
                    VALUES (?, ?, ?, ?)
                """, (current_date, chat_id, username, review))
            
            conn.commit()

        # Thank the user
        await message.answer("Thank you for your review! 🙏", reply_markup=main_menu_customer_keyboard)
    except sqlite3.Error as e:
        await message.answer(f"❌ Failed to save your review. Error: {e}", reply_markup=main_menu_customer_keyboard)

    # Clear the state
    await state.clear()

# Register the review handlers
dp.callback_query.register(handle_review, StateFilter(ReviewState.waiting_for_review))
dp.message.register(save_review, StateFilter(ReviewState.waiting_for_review))

############################



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
