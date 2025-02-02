from core_bot.core_bot import *
from bot_buttons.bot_buttons import *
from aiogram.utils.markdown import bold
from aiogram.types import CallbackQuery
import sqlite3
import datetime


# BASKET

async def handle_my_basket(callback_query: types.CallbackQuery, state: FSMContext):
    current_date = datetime.datetime.now().strftime(
        date_mask)  # Get current date in YYYY-MM-DD format
    chat_id = callback_query.message.chat.id
    unpaid_total_price = 0
    paid_total_price = 0
    total_price = 0
    all_time_unpaid_total_price = 0


    user_languages.setdefault(chat_id, default_lang)
    selected_language = user_languages.get(chat_id, default_lang)
    main_menu_customer_keyboard = create_customer_menu_buttons(chat_id, user_languages)
    
    debt_btn_str = get_translation("debt_btn_str", selected_language)
    total_btn_str = get_translation("total_btn_str", selected_language)
    main_menu_str = get_translation("main_menu_str", selected_language)
    make_payment_btn_str = get_translation("make_payment_btn_str", selected_language)
    your_basket_info_str = get_translation("your_basket_info_str", selected_language)
    have_unpaid_orders_info_str = get_translation("have_unpaid_orders_info_str", selected_language)
    have_paid_orders_info_str = get_translation("have_paid_orders_info_str", selected_language)
    order_paid_info_str = get_translation("order_paid_info_str", selected_language)
    empty_basket_info_str = get_translation("empty_basket_info_str", selected_language)


    try:
        with sqlite3.connect(database_location) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT ordered_item, ordered_quantity, total_price, ordered_item_id FROM Customers_Order WHERE date = ? AND chat_id = ? and is_paid = 0", (current_date, chat_id))
            rows = cursor.fetchall()

            'previous unpaid orders'
            cursor.execute(
                "SELECT ordered_item, ordered_quantity, total_price, ordered_item_id FROM Customers_Order WHERE date != ? AND chat_id = ? and is_paid = 0", (current_date, chat_id))
            unpaid_debt_rows = cursor.fetchall()

            # cursor.execute(
            #         "SELECT items_id FROM Lunch WHERE items = ?", (item_id))
            # item_name = cursor.fetchone()[0]

            cursor.execute(
                "SELECT ordered_item, ordered_quantity, total_price, ordered_item_id FROM Customers_Order WHERE date = ? AND chat_id = ? and is_paid = 1", (current_date, chat_id))
            paied_rows_for_today = cursor.fetchall()

            keyboard_paid = None
            if paied_rows_for_today:
                'fill it!'
                for row in paied_rows_for_today:
                    paid_total_price += row[2]
                # print(f'this is total unpaid price: {unpaid_total_price}')
                keyboard_paid = InlineKeyboardMarkup(inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text=f"{qnt} x {item[:MAX_TEXT_LENGTH]}={price} KGS", callback_data=f"select_{itemx_id}"
                        ),
                        
                    ]
                    for item, qnt, price, itemx_id in paied_rows_for_today
                ])

            keyboard_unpaid = None
            if unpaid_debt_rows:
                # print(f'unpaid rows: {unpaid_rows}')
                for row in unpaid_debt_rows:
                    unpaid_total_price += row[2]
                # print(f'this is total unpaid price: {unpaid_total_price}')
                keyboard_unpaid = InlineKeyboardMarkup(inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text=f"{qnt} x {item[:MAX_TEXT_LENGTH]}={price} KGS", callback_data=f"select_{itemx_id}"
                        ),
                        
                    ]
                    for item, qnt, price, itemx_id in unpaid_debt_rows
                ])

            if rows:
                # print(f'unpaid rows: {rows}')

                for row in rows:
                    total_price += row[2]
                    # print(row)
                # print(f'this is total price: {total_price}')
                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text=f"{qnt} x {item[:MAX_TEXT_LENGTH]} - {price} KGS", callback_data=f"select_{item_id}"
                        ),
                        InlineKeyboardButton(
                            text="❌", callback_data=f"delete_{item_id}"
                        )
                    ]
                    for item, qnt, price, item_id in rows
                ])
                all_time_unpaid_total_price = total_price + unpaid_total_price
                keyboard.inline_keyboard.append([InlineKeyboardButton(
                    text=debt_btn_str.format(unpaid_total_price), callback_data="noop")])
                keyboard.inline_keyboard.append([InlineKeyboardButton(
                    text=total_btn_str.format(all_time_unpaid_total_price), callback_data="noop")])
                keyboard.inline_keyboard.append([InlineKeyboardButton(
                    text=make_payment_btn_str, callback_data="pay_button")])
                keyboard.inline_keyboard.append([InlineKeyboardButton(
                    text=main_menu_str, callback_data="return_main_menu")])
                await callback_query.message.edit_text(your_basket_info_str.format(current_date),
                    reply_markup=keyboard
                )
                await state.set_state(BasketState.viewing_basket)

            elif keyboard_unpaid:
                all_time_unpaid_total_price = total_price + unpaid_total_price
                keyboard_unpaid.inline_keyboard.append([InlineKeyboardButton(
                    text=total_btn_str.format(all_time_unpaid_total_price), callback_data="noop")])
                keyboard_unpaid.inline_keyboard.append([InlineKeyboardButton(
                    text=make_payment_btn_str, callback_data="pay_button")])
                keyboard_unpaid.inline_keyboard.append([InlineKeyboardButton(
                    text=main_menu_str, callback_data="return_main_menu")])
                await callback_query.message.edit_text(have_unpaid_orders_info_str.format(current_date), reply_markup=keyboard_unpaid)
                await state.set_state(BasketState.viewing_basket)
            elif keyboard_paid:
                keyboard_paid.inline_keyboard.append([InlineKeyboardButton(
                    text=have_paid_orders_info_str.format(current_date, paid_total_price), callback_data="noop")])

                keyboard_paid.inline_keyboard.append([InlineKeyboardButton(
                    text=main_menu_str, callback_data="return_main_menu")])
                await callback_query.message.edit_text(order_paid_info_str.format(current_date), reply_markup=keyboard_paid)
                await state.set_state(BasketState.viewing_basket)
            else:

                await callback_query.message.edit_text(empty_basket_info_str.format(current_date), reply_markup=main_menu_customer_keyboard)
                await callback_query.answer()
                await state.clear()

    except sqlite3.Error as e:
        await callback_query.message.edit_text(f"❌ Database error: {e}")
        await state.clear()
    await callback_query.answer()


@dp.callback_query(BasketState.viewing_basket)
async def update_basket(callback_query: CallbackQuery, state: FSMContext):

    chat_id = callback_query.from_user.id
    user_languages.setdefault(chat_id, default_lang)
    selected_language = user_languages.get(chat_id, default_lang)
    main_menu_customer_keyboard = create_customer_menu_buttons(chat_id, user_languages)
    
    customer_menu_options_str = get_translation("customer_menu_options_str", selected_language)
    delete_orders_time_warning_str = get_translation("delete_orders_time_warning_str", selected_language)
    item_removed_str = get_translation("item_removed_str", selected_language)
    item_not_found_str = get_translation("item_not_found_str", selected_language)
    payment_time_warning_str = get_translation("payment_time_warning_str", selected_language)
    pay_cash_str = get_translation("pay_cash_str", selected_language)
    pay_card_str = get_translation("pay_card_str", selected_language)
    main_menu_str = get_translation("main_menu_str", selected_language)
    select_payment_method_str = get_translation("select_payment_method_str", selected_language)

    data = callback_query.data
    current_date = datetime.datetime.now().strftime(date_mask)

    if data == "return_main_menu":
        await state.clear()
        await callback_query.message.edit_text(
            customer_menu_options_str,
            reply_markup=main_menu_customer_keyboard
        )
        return

    if data.startswith("delete_"):
        now = datetime.datetime.now().time()
        if now >= ORDER_TIME_LIMIT:
            await callback_query.answer(
                delete_orders_time_warning_str.format(hour_time_limit, min_time_limit),
                show_alert=True
            )
            return

        item_id = data.split("_", 1)[1]
        # print(f'Deleting item: {item_id} | Chat ID: {chat_id} | Date: {current_date}')

        try:
            with sqlite3.connect(database_location) as conn:
                cursor = conn.cursor()

                # Get the quantity of the item to be restored
                cursor.execute("""
                    SELECT ordered_quantity 
                    FROM Customers_Order
                    WHERE date = ? AND chat_id = ? AND ordered_item_id = ?
                """, (current_date, chat_id, item_id))
                row = cursor.fetchone()

                if row:
                    ordered_quantity = row[0]

                    # Restore available amount in the Lunch table
                    cursor.execute("""
                        UPDATE Lunch
                        SET available_amount = available_amount + ?
                        WHERE date = ? AND items_id = ?
                    """, (ordered_quantity, current_date, item_id))

                    # Delete the item from the basket
                    cursor.execute("""
                        DELETE FROM Customers_Order
                        WHERE date = ? AND chat_id = ? AND ordered_item_id = ?
                    """, (current_date, chat_id, item_id))

                    conn.commit()

                    await callback_query.answer(item_removed_str)
                    # Refresh the basket view
                    await handle_my_basket(callback_query, state)
                else:
                    await callback_query.answer(item_not_found_str, show_alert=True)

        except sqlite3.Error as e:
            await callback_query.message.edit_text(f"❌ Database error: {e}")
            await state.clear()

    if data == "pay_button":
        now = datetime.datetime.now().time()
        if now < PAYMENT_TIME_LIMIT:
            await callback_query.answer(
                payment_time_warning_str.format(hour_time_limit, min_time_limit),
                show_alert=True
            )
            return

        cash_payment_btn = InlineKeyboardButton(
            text=pay_cash_str, callback_data='paid_cash')

        card_payment_btn = InlineKeyboardButton(
            text=pay_card_str, callback_data='paid_card')

        payment_keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [cash_payment_btn, card_payment_btn],
        ])
        payment_keyboard.inline_keyboard.append([InlineKeyboardButton(
            text=main_menu_str, callback_data="return_main_menu")])

        await callback_query.message.edit_text(
            select_payment_method_str,
            reply_markup=payment_keyboard
        )
        await state.set_state(BasketState.cash_or_card_qn)

    # await callback_query.answer()
    # await state.clear()


@dp.callback_query(BasketState.cash_or_card_qn)
async def handle_cash_payment(callback_query: types.CallbackQuery, state: FSMContext):
    chat_id = callback_query.from_user.id
    user_languages.setdefault(chat_id, default_lang)
    selected_language = user_languages.get(chat_id, default_lang)
    main_menu_customer_keyboard = create_customer_menu_buttons(chat_id, user_languages)

    customer_menu_options_str = get_translation("customer_menu_options_str", selected_language)
    cash_payment_complete_str = get_translation("cash_payment_complete_str", selected_language)
    upload_photo_receipt_str = get_translation("upload_photo_receipt_str", selected_language)
    # print('in cash handler')
    data = callback_query.data
    if data == "return_main_menu":
        await state.clear()
        await callback_query.message.edit_text(
            customer_menu_options_str,
            reply_markup=main_menu_customer_keyboard
        )
        return

    current_date = datetime.datetime.now().strftime(date_mask)
    if data == 'paid_cash':

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

            await callback_query.message.edit_text(cash_payment_complete_str, reply_markup=main_menu_customer_keyboard)
            await state.clear()

        except sqlite3.Error as e:
            await callback_query.message.edit_text(f"❌ Database error: {e}")
            await state.clear()
    if data == 'paid_card':
        # print('in paid card !!')
        await callback_query.message.edit_text(upload_photo_receipt_str)
        await state.set_state(BasketState.upload_receipt)

    await callback_query.answer()


async def handle_receipt_upload(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    # chat_id = callback_query.from_user.id
    user_languages.setdefault(chat_id, default_lang)
    selected_language = user_languages.get(chat_id, default_lang)
    main_menu_customer_keyboard = create_customer_menu_buttons(chat_id, user_languages)

    error_upload_photo_str = get_translation("error_upload_photo_str", selected_language)
    success_upload_photo_str = get_translation("success_upload_photo_str", selected_language)
    cancel_upload_photo_str = get_translation("cancel_upload_photo_str", selected_language)
    # Check for cancellation command
    if message.text and message.text.lower() == "/start":
        await message.answer(cancel_upload_photo_str, reply_markup=main_menu_customer_keyboard)
        await state.clear()
        return
    current_date = datetime.datetime.now().strftime(date_mask)
    try:
        file_id = None
        file_name = None

        if message.document:  # File upload
            file_id = message.document.file_id
            file_name = message.document.file_name
        elif message.photo:  # Photo upload
            file_id = message.photo[-1].file_id  # Get highest resolution photo
            file_name = f"{message.from_user.id}_photo.jpg"
        else:
            await message.answer(error_upload_photo_str)
            return
        if file_id:
            file = await message.bot.get_file(file_id)
            file_path = f"raw_data/payment_screenshots/{current_date}_{file_name}"
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            # Download the file
            await message.bot.download_file(file.file_path, file_path)

            with open(file_path, 'rb') as file_:
                blob_data = file_.read()

            # Success response
            try:
                with sqlite3.connect(database_location) as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        UPDATE Customers_Order
                        SET is_paid = 1,
                        payment_type = 'card',
                        screenshot = ?
                        WHERE chat_id = ? AND is_paid = 0
                    """, (blob_data, chat_id,))
                    conn.commit()

                await message.answer(success_upload_photo_str, reply_markup=main_menu_customer_keyboard)
                await state.clear()

            except sqlite3.Error as e:
                await message.answer(f"❌ Database error: {e}")
                await state.clear()

    except Exception as e:
        # Error handling
        await message.answer(f"❌ Error saving receipt: {e}")
        await state.clear()

# Register the review handlers
dp.callback_query.register(
    handle_cash_payment, StateFilter(BasketState.upload_receipt))
dp.message.register(handle_receipt_upload,
                    StateFilter(BasketState.upload_receipt))

############################
