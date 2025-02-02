from core_bot.core_bot import *
from bot_buttons.bot_buttons import *
from aiogram.utils.markdown import bold
from aiogram.types import CallbackQuery
import sqlite3
import datetime


######################Additions
'garnish'
async def handle_specify_additions(callback_query: types.CallbackQuery, state: FSMContext): 
    # chat_id = message.chat.id
    chat_id = callback_query.from_user.id
    user_languages.setdefault(chat_id, default_lang)
    selected_language = user_languages.get(chat_id, default_lang)
    main_menu_customer_keyboard = create_customer_menu_buttons(chat_id, user_languages)

    order_time_warning_str = get_translation("order_time_warning_str", selected_language)
    main_menu_str = get_translation("main_menu_str", selected_language)
    empty_basket_info_str = get_translation("empty_basket_info_str", selected_language)
    select_following_options_str = get_translation("select_following_options_str", selected_language)


    now = datetime.datetime.now().time()
    if now > ORDER_TIME_LIMIT:
        await callback_query.answer(order_time_warning_str.format(hour_time_limit, min_time_limit), show_alert=True)
        return
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
                        ]
                        for row in rows
                    ]
                )
                keyboard.inline_keyboard.append([InlineKeyboardButton(
                    text=main_menu_str, callback_data="return_main_menu")])
                await callback_query.message.edit_text(
                    select_following_options_str,
                    reply_markup=keyboard
                )
                await state.set_state(AdditionsState.selecting_lunch)
            else:
                await callback_query.message.edit_text(empty_basket_info_str.format(current_date), reply_markup=main_menu_customer_keyboard)
                await callback_query.answer()
                await state.clear()
    except sqlite3.Error as e:
        await callback_query.message.edit_text(f"❌ Database error: {e}")
        await state.clear()
    await callback_query.answer()

@dp.callback_query(AdditionsState.selecting_lunch)
async def handle_addition_selection(callback_query: types.CallbackQuery, state: FSMContext):
    # chat_id = message.chat.id
    chat_id = callback_query.from_user.id
    user_languages.setdefault(chat_id, default_lang)
    selected_language = user_languages.get(chat_id, default_lang)
    main_menu_customer_keyboard = create_customer_menu_buttons(chat_id, user_languages)

    customer_menu_options_str = get_translation("customer_menu_options_str", selected_language)
    add_garnish_str = get_translation("add_garnish_str", selected_language)

    current_date = datetime.datetime.now().strftime(
        date_mask)
    if callback_query.data == "return_main_menu":
        await state.clear()
        await callback_query.message.edit_text(
            customer_menu_options_str,
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
            # print(f'this is item ID: {item_id}')

            # Fetch the price of the item from the Menu table
            cursor.execute(
                """
                SELECT items FROM Lunch WHERE items_id = ? and date = ?
                """, (item_id, current_date,)  # Pass item_id twice
            )

            item_name = cursor.fetchone()[0]

            # print(f'item_name is {item_name}')


        # Prompt the user to enter additional info
        await callback_query.message.edit_text(add_garnish_str.format(item_name))
        await state.set_state(AdditionsState.waiting_for_addition)
        await callback_query.answer()

async def save_additional_info(message: types.Message, state: FSMContext):

    

    chat_id = message.chat.id
    # chat_id = callback_query.from_user.id
    user_languages.setdefault(chat_id, default_lang)
    selected_language = user_languages.get(chat_id, default_lang)
    main_menu_customer_keyboard = create_customer_menu_buttons(chat_id, user_languages)
    confirm_garnish_str = get_translation("confirm_garnish_str", selected_language)
    canceled_str = get_translation("canceled_str", selected_language)

    if message.text and message.text.lower() == "/start":
        await message.answer(canceled_str, reply_markup=main_menu_customer_keyboard)
        await state.clear()
        return
    
    current_date = datetime.datetime.now().strftime(
        date_mask)
    # Get the user's input
    addition = message.text

    # Retrieve the item and other necessary data from the state
    data = await state.get_data()
    item_id = data.get("selected_item")
    chat_id = message.chat.id
    current_date = datetime.datetime.now().strftime(date_mask)

    try:
        with sqlite3.connect(database_location) as conn:
            cursor = conn.cursor()
            
            cursor.execute(
                """
                SELECT items FROM Lunch WHERE items_id = ? and date = ?

                """, (item_id, current_date,)  # Pass item_id twice
            )

            item_name = cursor.fetchone()[0]

            # Update the additional_info for the selected item
            cursor.execute("""
                UPDATE Customers_Order
                SET additional_info = ?
                WHERE date = ? AND chat_id = ? AND ordered_item_id = ?
            """, (addition, current_date, chat_id, item_id))
            conn.commit()

        # Notify the user
        await message.answer(confirm_garnish_str.format(item_name), reply_markup=main_menu_customer_keyboard)
    except sqlite3.Error as e:
        await message.answer(f"❌ Failed to save additional info. Error: {e}", reply_markup=main_menu_customer_keyboard)

    # Clear the state after processing
    await state.clear()

dp.callback_query.register(handle_specify_additions, StateFilter(AdditionsState.selecting_lunch))
dp.callback_query.register(handle_addition_selection, StateFilter(AdditionsState.selecting_lunch))
dp.message.register(save_additional_info, StateFilter(AdditionsState.waiting_for_addition))
