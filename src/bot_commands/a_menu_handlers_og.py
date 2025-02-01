from core_bot.core_bot import *
from bot_buttons.bot_buttons import *
from aiogram.utils.markdown import bold
from aiogram.types import CallbackQuery
import sqlite3
import datetime
import re

# Admin action handlers

# editing lunch


async def handle_editing_lunch_menu(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.answer(
        "Please send the lunch menu details in the format:\n"
        "\n10 Manty 250"
        "\nPasta",
        parse_mode="Markdown",
    )
    await state.set_state(EditLunchMenuState.waiting_for_menu_text)


@dp.message(EditLunchMenuState.waiting_for_menu_text)
async def handle_reset_lunch_menu(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    # chat_id = callback_query.from_user.id
    user_languages.setdefault(chat_id, default_lang)
    selected_language = user_languages.get(chat_id, default_lang)
    main_menu_admin_keyboard = create_admin_menu_buttons(chat_id, user_languages)

    input_text = message.text.strip()
    current_date = datetime.datetime.now().strftime(date_mask)  # Get current date
    menu_items = input_text.split("\n")  # Split by newlines

    if not menu_items:  # Validate input menu text
        await message.answer("❌ The provided menu is empty. Please provide a valid menu.")
        return

    try:
        with sqlite3.connect(database_location) as conn:
            conn.isolation_level = None  # Enable manual transaction control
            cursor = conn.cursor()
            cursor.execute("BEGIN TRANSACTION;")  # Begin transaction

            # Step 1: Delete the current menu for today
            cursor.execute("DELETE FROM Lunch WHERE date = ?", (current_date,))

            # Step 2: Insert the new menu items
            for items_id, item in enumerate(menu_items):
                item = item.strip()
                if not item:  # Skip empty or whitespace-only lines
                    continue

                # Extract item name and price (default to FIXED_PRICE_Lunch if not provided)
                match = re.match(r'^(.+?)(?:\s+(\d+))?$', item)
                if match:
                    item_name = match.group(1).strip()
                    price = int(match.group(2)) if match.group(
                        2) else FIXED_PRICE_Lunch

                    cursor.execute(
                        "INSERT INTO Lunch (date, items_id, items, price) VALUES (?, ?, ?, ?)",
                        (current_date, f'lunch{items_id}', item_name, price),
                    )

            conn.commit()  # Commit all changes

            # Step 3: Notify the user
            menu_display = "\n".join(
                f"- {match.group(1).strip()} (Price: {match.group(2) if match.group(2) else FIXED_PRICE_Lunch})"
                for match in (re.match(r'^(.+?)(?:\s+(\d+))?$', item.strip()) for item in menu_items)
                if match
            )
            await message.answer(
                f"✅ Menu reset for {current_date}:\n{menu_display}",
                reply_markup=main_menu_admin_keyboard
            )

    except sqlite3.Error as e:
        await message.answer(f"❌ Database error: {str(e)}")
        if 'conn' in locals():
            conn.rollback()  # Rollback changes if a database error occurs
    except Exception as e:
        await message.answer(f"❌ An unexpected error occurred: {str(e)}. Please contact support.")
    finally:
        await state.clear()  # Clear the state to reset the flow


async def handle_showing_current_lunch_menu(callback_query: CallbackQuery):
    # chat_id = message.chat.id
    chat_id = callback_query.from_user.id
    user_languages.setdefault(chat_id, default_lang)
    selected_language = user_languages.get(chat_id, default_lang)
    main_menu_admin_keyboard = create_admin_menu_buttons(chat_id, user_languages)
    current_date = datetime.datetime.now().strftime(
        date_mask)  # Get current date in YYYY-MM-DD format

    try:
        with sqlite3.connect(database_location) as conn:
            cursor = conn.cursor()
            # Use parameterized query to prevent SQL injection
            cursor.execute(
                "SELECT items, price FROM Lunch WHERE date = ? order by items", (current_date,))
            rows = cursor.fetchall()

        if rows:
            # Format the menu into a readable string
            menu = "\n".join(
                [f"- {item} (Price: {price})" for item, price in rows])
            await callback_query.message.edit_text(f"```🍴 Today's Lunch Menu ({current_date}):\n{menu}```", reply_markup=main_menu_admin_keyboard, parse_mode="MarkdownV2")
        else:
            await callback_query.message.edit_text(f"⚠️ No lunch menu available for {current_date}.", reply_markup=main_menu_admin_keyboard)
    except sqlite3.Error as e:
        await callback_query.message.edit_text(f"❌ Database error: {e}", reply_markup=main_menu_admin_keyboard)
    # await callback_query.message.edit_text(
    #     "Performing another admin action!",
    #     reply_markup=main_menu_admin_keyboard,
    # )
#####################


# # Editing bakery
# async def handle_editing_bakery_menu(callback_query: types.CallbackQuery, state: FSMContext):
#     await callback_query.message.answer(
#         "Please send the Bakery menu details in the format:\n"
#         "Sochinskie\n"
#         "Bulochka\n",
#         parse_mode="Markdown",
#     )
#     await state.set_state(EditBakeryMenuState.waiting_for_menu_text)


# @dp.message(EditBakeryMenuState.waiting_for_menu_text)
# async def handle_reset_bakery_menu(message: types.Message, state: FSMContext):
#     input_text = message.text.strip()
#     current_date = datetime.datetime.now().strftime(date_mask)  # Get current date
#     menu_items = input_text.split("\n")  # Split by newlines

#     if not menu_items:  # Validate input menu text
#         await message.answer("❌ The provided bakery menu is empty. Please provide a valid menu.")
#         return

#     try:
#         with sqlite3.connect(database_location) as conn:
#             conn.isolation_level = None  # Enable manual transaction control
#             cursor = conn.cursor()
#             cursor.execute("BEGIN TRANSACTION;")  # Begin transaction

#             # Step 1: Delete the current menu for today
#             cursor.execute("DELETE FROM Bakery WHERE date = ?",
#                            (current_date,))

#             # Step 2: Insert the new menu items
#             for item_id, item in enumerate(menu_items):
#                 item = item.strip()  # Clean up whitespace
#                 if not item:  # Skip empty or whitespace-only lines
#                     continue

#                 # Extract item name and price (default to FIXED_PRICE_Bakery if not provided)
#                 match = re.match(r'^(.+?)(?:\s+(\d+))?$', item)
#                 if match:
#                     item_name = match.group(1).strip()
#                     price = int(match.group(2)) if match.group(
#                         2) else FIXED_PRICE_Bakery

#                     cursor.execute(
#                         "INSERT INTO Bakery (date, items_id, items, price) VALUES (?, ?, ?, ?)",
#                         (current_date, f'bakery{item_id}', item_name, price),
#                     )

#             conn.commit()  # Commit all changes

#             # Step 3: Notify the user
#             menu_display = "\n".join(
#                 f"- {match.group(1).strip()} (Price: {match.group(2) if match.group(2) else FIXED_PRICE_Bakery})"
#                 for match in (re.match(r'^(.+?)(?:\s+(\d+))?$', item.strip()) for item in menu_items)
#                 if match
#             )
#             await message.answer(
#                 f"✅ Bakery Menu reset for {current_date}:\n{menu_display}",
#                 reply_markup=main_menu_admin_keyboard
#             )

#     except sqlite3.Error as e:
#         await message.answer(f"❌ Database error: {str(e)}")
#         if 'conn' in locals():
#             conn.rollback()  # Rollback changes if a database error occurs
#     except Exception as e:
#         await message.answer(f"❌ An unexpected error occurred: {str(e)}. Please contact support.")
#     finally:
#         await state.clear()  # Clear the state to reset the flow


# async def handle_showing_current_bakery_menu(callback_query: CallbackQuery):
#     current_date = datetime.datetime.now().strftime(
#         date_mask)  # Get current date in YYYY-MM-DD format

#     try:
#         with sqlite3.connect(database_location) as conn:
#             cursor = conn.cursor()
#             # Use parameterized query to prevent SQL injection
#             cursor.execute(
#                 "SELECT items, price FROM Bakery WHERE date = ?", (current_date,))
#             rows = cursor.fetchall()

#         if rows:
#             # Format the menu into a readable string
#             menu = "\n".join(
#                 [f"- {item} (Price: {price})" for item, price in rows])
#             print(menu)
#             await callback_query.message.edit_text(f"🍴 Today's Bakery Menu ({current_date}):\n{menu}", reply_markup=main_menu_admin_keyboard)
#         else:
#             await callback_query.message.edit_text(f"⚠️ No Bakery menu available for {current_date}.", reply_markup=main_menu_admin_keyboard)
#     except sqlite3.Error as e:
#         await callback_query.message.edit_text(f"❌ Database error: {e}", reply_markup=main_menu_admin_keyboard)
