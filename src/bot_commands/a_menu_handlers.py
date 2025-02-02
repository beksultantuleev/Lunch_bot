from core_bot.core_bot import *
from bot_buttons.bot_buttons import *
from aiogram.utils.markdown import bold
from aiogram.types import CallbackQuery
import sqlite3
import datetime
import re
import pandas as pd
from aiogram.types import CallbackQuery, FSInputFile
from io import BytesIO
import xlsxwriter

# Admin action handlers

# editing lunch


async def handle_editing_lunch_menu(callback_query: types.CallbackQuery, state: FSMContext):
    chat_id = callback_query.from_user.id
    user_languages.setdefault(chat_id, default_lang)
    selected_language = user_languages.get(chat_id, default_lang)

    reset_lunch_menu_info_str = get_translation("reset_lunch_menu_info_str", selected_language)
    await callback_query.message.answer(
        reset_lunch_menu_info_str,
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
    canceled_str = get_translation("canceled_str", selected_language)
    error_empty_given_menu_str = get_translation("error_empty_given_menu_str", selected_language)
    menu_successfully_updated_str = get_translation("menu_successfully_updated_str", selected_language)

    if message.text and message.text.lower() == "/start":
        await message.answer(canceled_str, reply_markup=main_menu_admin_keyboard)
        await state.clear()
        return
    input_text = message.text.strip()
    current_date = datetime.datetime.now().strftime(date_mask)  # Get current date
    menu_items = input_text.split("\n")  # Split by newlines

    if not menu_items:
        await message.answer(error_empty_given_menu_str)
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
                if not item:
                    continue

                # Match format: "<available_amount> <item_name> <price>"
                match = re.match(r'^(\d+)?\s*(.+?)\s*(\d+)?$', item)
                if match:
                    available_amount = int(match.group(1)) if match.group(1) else DEFAULT_AVAILABLE_AMOUNT
                    item_name = match.group(2).strip()
                    price = int(match.group(3)) if match.group(3) else FIXED_PRICE_Lunch

                    cursor.execute(
                        "INSERT INTO Lunch (date, items_id, items, price, available_amount) VALUES (?, ?, ?, ?, ?)",
                        (current_date, f'lunch{items_id}', item_name, price, available_amount),
                    )

            conn.commit()  # Commit all changes

            menu_display = "\n".join(
                f"- {match.group(2).strip()} (Available: {match.group(1) if match.group(1) else DEFAULT_AVAILABLE_AMOUNT}, Price: {match.group(3) if match.group(3) else FIXED_PRICE_Lunch})"
                for match in (re.match(r'^(?:(\d+)\s+)?(.+?)\s+(\d+)?$', item.strip()) for item in menu_items)
                if match
            )
            await message.answer(
                f"{menu_successfully_updated_str.format(current_date)}:\n{menu_display}",
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
    no_lunch_info_str = get_translation("no_lunch_info_str", selected_language)
    current_lunch_menu_str = get_translation("current_lunch_menu_str", selected_language)

    current_date = datetime.datetime.now().strftime(
        date_mask)  

    try:
        with sqlite3.connect(database_location) as conn:
            cursor = conn.cursor()
            # Use parameterized query to prevent SQL injection
            cursor.execute(
                "SELECT items, price, available_amount FROM Lunch WHERE date = ? order by items", (current_date,))
            rows = cursor.fetchall()

        if rows:
            # Format the menu into a readable string
            menu = "\n".join(
                [f"- ({int(available_amount)}) x {item} (Price: {price})" for item, price, available_amount in rows])
            await callback_query.message.edit_text(f"```\n{current_lunch_menu_str} ({current_date}):\n{menu}```", reply_markup=main_menu_admin_keyboard, parse_mode="MarkdownV2")
        else:
            await callback_query.message.edit_text(no_lunch_info_str.format(current_date), reply_markup=main_menu_admin_keyboard)
    except sqlite3.Error as e:
        await callback_query.message.edit_text(f"❌ Database error: {e}", reply_markup=main_menu_admin_keyboard)




async def handle_today_export_orders(callback_query: CallbackQuery):
    current_date = datetime.datetime.now().strftime(date_mask)  
    file_name = f"raw_data/export_file/Orders_{current_date}.xlsx"

    try:
        with sqlite3.connect(database_location) as conn:
            cursor = conn.cursor()

            # Fetch required columns including screenshot
            cursor.execute("""
                SELECT date, username, ordered_item, additional_info, 
                       ordered_quantity, unit_price, total_price, 
                       CASE WHEN is_paid = 1 THEN 'Paid' ELSE 'Unpaid' END as is_paid, 
                       payment_type, screenshot
                FROM Customers_Order
                where date = ?
                ORDER BY date DESC, username ASC
            """, (current_date,))
            rows = cursor.fetchall()

        # Prepare data for Excel
        excel_data = []
        image_data = []  # To store image BLOBs

        for row in rows:
            date, username, item, info, qty, price, total, is_paid, payment_type, screenshot = row
            excel_data.append([date, username, item, info, qty, price, total, is_paid, payment_type])
            image_data.append(screenshot)  # Store image data

        # Convert to DataFrame
        df = pd.DataFrame(excel_data, columns=[
            "Date", "Username", "Ordered Item", "Additional Info",
            "Quantity", "Unit Price", "Total Price", "Payment Status", "Payment Type"
        ])

        # Save to Excel with images
        with pd.ExcelWriter(file_name, engine="xlsxwriter") as writer:
            df.to_excel(writer, sheet_name="Orders", index=False)

            workbook = writer.book
            worksheet = writer.sheets["Orders"]

            # Set column width for the screenshot column
            image_column = len(df.columns)  # Next column for images
            worksheet.set_column(image_column, image_column, 20)  # Adjust width for images
            worksheet.write(0, image_column, "Screenshot")  # Add header

            row_num = 1  # Start from row 2 (row 1 is header)
            for screenshot in image_data:
                if screenshot:
                    image_stream = BytesIO(screenshot)  # Convert BLOB to image

                    # Dynamically set row height based on image size
                    worksheet.set_row(row_num, 100)  # Set row height for images

                    # Insert image inside the cell with proper alignment
                    worksheet.insert_image(
                        row_num, image_column, f"screenshot_{row_num}.png",
                        {
                            'image_data': image_stream,
                            'x_offset': 2, 'y_offset': 2,  # Adjust positioning inside cell
                            'x_scale': 0.7, 'y_scale': 0.7,  # Resize image to fit cell
                            'positioning': 1  # Ensures the image stays inside the cell
                        }
                    )
                row_num += 1

        # Send the Excel file
        file_to_send = FSInputFile(file_name)
        await callback_query.message.answer_document(file_to_send,)
        os.remove(file_name)

    except sqlite3.Error as e:
        await callback_query.message.edit_text(f"❌ Database error: {e}")



async def handle_all_export_orders(callback_query: CallbackQuery):
    # chat_id = message.chat.id
    chat_id = callback_query.from_user.id
    user_languages.setdefault(chat_id, default_lang)
    selected_language = user_languages.get(chat_id, default_lang)
    main_menu_admin_keyboard = create_admin_menu_buttons(chat_id, user_languages)
    current_date = datetime.datetime.now().strftime(
        date_mask)
    file_name = f"raw_data/export_file/Orders_{current_date}.xlsx"

    try:
        with sqlite3.connect(database_location) as conn:
            cursor = conn.cursor()

            # Fetch required columns
            cursor.execute("""
                SELECT date, username, ordered_item, additional_info, 
                       ordered_quantity, unit_price, total_price, 
                       CASE WHEN is_paid = 1 THEN 'Paid' ELSE 'Unpaid' END as is_paid, 
                       payment_type
                FROM Customers_Order
                ORDER BY date DESC, username ASC
            """)
            rows = cursor.fetchall()

            # Convert to DataFrame
            df = pd.DataFrame(rows, columns=[
                "Date", "Username", "Ordered Item", "Additional Info",
                "Quantity", "Unit Price", "Total Price", "Payment Status", "Payment Type"
            ])

            # Save DataFrame to Excel
            df.to_excel(file_name, index=False)

        # Send the file
        file_to_send = FSInputFile(file_name)
        await callback_query.message.answer_document(file_to_send,)
        os.remove(file_name)

    except sqlite3.Error as e:
        await callback_query.message.edit_text(f"❌ Database error: {e}", reply_markup=main_menu_admin_keyboard)