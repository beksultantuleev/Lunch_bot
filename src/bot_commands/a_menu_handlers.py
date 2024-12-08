from core_bot.core_bot import *
from bot_buttons.bot_buttons import *
from aiogram.utils.markdown import bold
from aiogram.types import CallbackQuery
import sqlite3
import datetime

# Admin action handlers

###############editing lunch
async def handle_editing_lunch_menu(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.answer(
        "Please send the lunch menu details in the format:\n"
        "Manty"
        "Pasta",
        parse_mode="Markdown",
    )
    await state.set_state(EditLunchMenuState.waiting_for_menu_text)


@dp.message(EditLunchMenuState.waiting_for_menu_text)
async def handle_reset_lunch_menu(message: types.Message, state: FSMContext):
    input_text = message.text.strip()
    current_date = datetime.datetime.now().strftime(date_mask)  # Get current date
    menu_items = input_text.split("\n")  # Split by newlines

    try:
        with sqlite3.connect(database_location) as conn:
            cursor = conn.cursor()

            # Step 1: Delete the current menu for today
            cursor.execute("DELETE FROM Lunch WHERE date = ?", (current_date,))

            # Step 2: Insert the new menu items
            for item in menu_items:
                item = item.strip()  # Clean up whitespace
                if not item:
                    continue  # Skip empty lines

                cursor.execute(
                    "INSERT INTO Lunch (date, items, price) VALUES (?, ?, ?)",
                    (current_date, item, FIXED_PRICE_Lunch),
                )

            conn.commit()  # Commit all changes at once

            # Step 3: Notify the user
            await message.answer(
                f"✅ Menu reset for {current_date}:\n" + "\n".join(f"- {item}" for item in menu_items if item),
                reply_markup=main_menu_admin_keyboard
            )

    except sqlite3.Error as e:
        await message.answer(f"❌ Database error: {str(e)}")
    except Exception as e:
        await message.answer(f"❌ An unexpected error occurred: {str(e)}")
    finally:
        await state.clear()


async def handle_showing_current_lunch_menu(callback_query: CallbackQuery):
    current_date = datetime.datetime.now().strftime(date_mask)  # Get current date in YYYY-MM-DD format

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
            await callback_query.message.edit_text(f"🍴 Today's Lunch Menu ({current_date}):\n{menu}", reply_markup=main_menu_admin_keyboard)
        else:
            await callback_query.message.edit_text(f"⚠️ No lunch menu available for {current_date}.", reply_markup=main_menu_admin_keyboard)
    except sqlite3.Error as e:
        await callback_query.message.edit_text(f"❌ Database error: {e}", reply_markup=main_menu_admin_keyboard)
    # await callback_query.message.edit_text(
    #     "Performing another admin action!",
    #     reply_markup=main_menu_admin_keyboard,
    # )
#####################




###################Editing bakery
async def handle_editing_bakery_menu(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.answer(
        "Please send the Bakery menu details in the format:\n"
        "Sochinskie\n"
        "Bulochka\n",
        parse_mode="Markdown",
    )
    await state.set_state(EditBakeryMenuState.waiting_for_menu_text)

@dp.message(EditBakeryMenuState.waiting_for_menu_text)
async def handle_reset_bakery_menu(message: types.Message, state: FSMContext):
    input_text = message.text.strip()
    current_date = datetime.datetime.now().strftime(date_mask)  # Get current date
    menu_items = input_text.split("\n")  # Split by newlines

    try:
        with sqlite3.connect(database_location) as conn:
            cursor = conn.cursor()

            # Step 1: Delete the current menu for today
            cursor.execute("DELETE FROM Bakery WHERE date = ?", (current_date,))

            # Step 2: Insert the new menu items
            for item in menu_items:
                item = item.strip()  # Clean up whitespace
                if not item:
                    continue  # Skip empty lines

                cursor.execute(
                    "INSERT INTO Bakery (date, items, price) VALUES (?, ?, ?)",
                    (current_date, item, FIXED_PRICE_Bakery),
                )

            conn.commit()  # Commit all changes at once

            # Step 3: Notify the user
            await message.answer(
                f"✅ Bakery Menu reset for {current_date}:\n" + "\n".join(f"- {item}" for item in menu_items if item),
                reply_markup=main_menu_admin_keyboard
            )

    except sqlite3.Error as e:
        await message.answer(f"❌ Database error: {str(e)}")
    except Exception as e:
        await message.answer(f"❌ An unexpected error occurred: {str(e)}")
    finally:
        await state.clear()


async def handle_showing_current_bakery_menu(callback_query: CallbackQuery):
    current_date = datetime.datetime.now().strftime(date_mask)  # Get current date in YYYY-MM-DD format

    try:
        with sqlite3.connect(database_location) as conn:
            cursor = conn.cursor()
            # Use parameterized query to prevent SQL injection
            cursor.execute(
                "SELECT items, price FROM Bakery WHERE date = ?", (current_date,))
            rows = cursor.fetchall()

        if rows:
            # Format the menu into a readable string
            menu = "\n".join(
                [f"- {item} (Price: {price})" for item, price in rows])
            print(menu)
            await callback_query.message.edit_text(f"🍴 Today's Bakery Menu ({current_date}):\n{menu}", reply_markup=main_menu_admin_keyboard)
        else:
            await callback_query.message.edit_text(f"⚠️ No Bakery menu available for {current_date}.", reply_markup=main_menu_admin_keyboard)
    except sqlite3.Error as e:
        await callback_query.message.edit_text(f"❌ Database error: {e}", reply_markup=main_menu_admin_keyboard)

