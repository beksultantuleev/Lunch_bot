from core_bot.core_bot import *
from bot_buttons.bot_buttons import *
from aiogram.utils.markdown import bold
from aiogram.types import CallbackQuery
import sqlite3
import datetime


# raiting
async def handle_rating(callback_query: types.CallbackQuery, state: FSMContext):
    # chat_id = message.chat.id
    chat_id = callback_query.from_user.id
    user_languages.setdefault(chat_id, default_lang)
    selected_language = user_languages.get(chat_id, default_lang)
    main_menu_customer_keyboard = create_customer_menu_buttons(chat_id, user_languages)
    rate_time_warning_str = get_translation("rate_time_warning_str", selected_language)
    main_menu_str = get_translation("main_menu_str", selected_language)
    rate_lunch_str = get_translation("rate_lunch_str", selected_language)
    empty_basket_info_str = get_translation("empty_basket_info_str", selected_language)

    now = datetime.datetime.now().time()
    if now < PAYMENT_TIME_LIMIT:
        await callback_query.answer(rate_time_warning_str.format(hour_time_limit, min_time_limit), show_alert=True)
        return

    current_date = datetime.datetime.now().strftime(date_mask)
    chat_id = callback_query.message.chat.id

    try:
        with sqlite3.connect(database_location) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT ordered_item_id, ordered_item 
                FROM Customers_Order 
                WHERE date = ? AND chat_id = ?
            """, (current_date, chat_id))

            rows = cursor.fetchall()

            if rows:
                # Create dynamic inline keyboard with lunch items
                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(
                        text=f"{row[1][:MAX_TEXT_LENGTH]}..." if len(
                            row[1]) > MAX_TEXT_LENGTH else row[1],
                        callback_data=f"select_{row[0]}"
                    )] for row in rows
                ])

                # Add "Return to Menu" button
                keyboard.inline_keyboard.append([
                    InlineKeyboardButton(
                        text=main_menu_str, callback_data="return_main_menu")
                ])

                await callback_query.message.edit_text(
                    f"{rate_lunch_str} {current_date}:",
                    reply_markup=keyboard
                )
                await state.set_state(RaitingState.selecting_lunch)
            else:
                await callback_query.message.edit_text(
                    empty_basket_info_str.format(current_date),
                    reply_markup=main_menu_customer_keyboard
                )
                await state.clear()
    except sqlite3.Error as e:
        await callback_query.message.edit_text(f"❌ Database error: {e}")
        await state.clear()
    await callback_query.answer()

@dp.callback_query(RaitingState.selecting_lunch)
async def handle_rating_selection(callback_query: types.CallbackQuery, state: FSMContext):
    current_date = datetime.datetime.now().strftime(date_mask)
    chat_id = callback_query.from_user.id
    user_languages.setdefault(chat_id, default_lang)
    selected_language = user_languages.get(chat_id, default_lang)
    main_menu_customer_keyboard = create_customer_menu_buttons(chat_id, user_languages)
    customer_menu_options_str = get_translation("customer_menu_options_str", selected_language)
    bad_rating_str = get_translation("bad_rating_str", selected_language)
    good_rating_str = get_translation("good_rating_str", selected_language)
    awesome_rating_str = get_translation("awesome_rating_str", selected_language)
    main_menu_str = get_translation("main_menu_str", selected_language)
    rate_item_str = get_translation("rate_item_str", selected_language)

    if callback_query.data == "return_main_menu":
        await state.clear()
        await callback_query.message.edit_text(
            customer_menu_options_str,
            reply_markup=main_menu_customer_keyboard
        )
        return

    if callback_query.data.startswith("select_"):
        item_id = callback_query.data.split("select_", 1)[1]

        with sqlite3.connect(database_location) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT ordered_item FROM Customers_Order 
                WHERE ordered_item_id = ? AND date = ?
            """, (item_id, current_date))

            row = cursor.fetchone()

            if row:
                item_name = row[0]
                # Store item_id in FSM context
                await state.update_data(selected_item_id=item_id, selected_item=item_name)

                # Create rating buttons
                rate_keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text=bad_rating_str, callback_data='rate_bad'),
                        InlineKeyboardButton(
                            text=good_rating_str, callback_data='rate_good'),
                        InlineKeyboardButton(
                            text=awesome_rating_str, callback_data='rate_awesome'),
                    ],
                    [InlineKeyboardButton(
                        text=main_menu_str, callback_data="return_main_menu")]
                ])

                await callback_query.message.edit_text(
                    rate_item_str.format(item_name),
                    reply_markup=rate_keyboard
                )
                await state.set_state(RaitingState.set_raiting)

        await callback_query.answer()

@dp.callback_query(RaitingState.set_raiting)
async def handle_rating_set(callback_query: types.CallbackQuery, state: FSMContext):

    chat_id = callback_query.message.chat.id
    user_languages.setdefault(chat_id, default_lang)
    selected_language = user_languages.get(chat_id, default_lang)
    main_menu_customer_keyboard = create_customer_menu_buttons(chat_id, user_languages)
    data = callback_query.data
    customer_menu_options_str = get_translation("customer_menu_options_str", selected_language)
    no_item_for_rating_str = get_translation("no_item_for_rating_str", selected_language)
    rating_complete_str = get_translation("rating_complete_str", selected_language)

    if data == "return_main_menu":
        await state.clear()
        await callback_query.message.edit_text(
            customer_menu_options_str,
            reply_markup=main_menu_customer_keyboard
        )
        return

    # Determine rating score
    rating_score = None
    if data == 'rate_awesome':
        rating_score = 5
    elif data == 'rate_good':
        rating_score = 3
    elif data == 'rate_bad':
        rating_score = 1

    if rating_score is not None:
        try:
            user_data = await state.get_data()
            selected_item_id = user_data.get("selected_item_id")
            selected_item = user_data.get("selected_item")

            if not selected_item_id or not selected_item:
                await callback_query.message.edit_text(
                    no_item_for_rating_str,
                    reply_markup=main_menu_customer_keyboard
                )
                await state.clear()
                return

            with sqlite3.connect(database_location) as conn:
                cursor = conn.cursor()

                # Ensure the rating table exists

                current_date = datetime.date.today()

                # Insert or update the rating
                cursor.execute("""
                    INSERT INTO Order_raiting (date, chat_id, username, ordered_item_id, ordered_item, raiting_score)
                    VALUES (?, ?, ?, ?, ?, ?)
                    ON CONFLICT(date, chat_id, ordered_item)
                    DO UPDATE SET raiting_score = excluded.raiting_score;
                """, (current_date, chat_id, callback_query.from_user.username, selected_item_id, selected_item, rating_score))

                conn.commit()

            # Confirmation message
            await callback_query.message.edit_text(
                rating_complete_str.format(selected_item, rating_score),
                reply_markup=main_menu_customer_keyboard
            )
            await state.clear()

        except sqlite3.Error as e:
            await callback_query.message.edit_text(f"❌ Database error: {e}")
            await state.clear()

################

async def handle_showing_rating_menu(callback_query: CallbackQuery):
    # chat_id = message.chat.id
    chat_id = callback_query.from_user.id
    user_languages.setdefault(chat_id, default_lang)
    selected_language = user_languages.get(chat_id, default_lang)
    main_menu_customer_keyboard = create_customer_menu_buttons(chat_id, user_languages)
    top_lunch_listing_str = get_translation("top_lunch_listing_str", selected_language)
    no_top_lunch_listing_str = get_translation("no_top_lunch_listing_str", selected_language)

    try:
        with sqlite3.connect(database_location) as conn:
            cursor = conn.cursor()

            # Fetch the top 20 highest-rated lunch items in the last 30 days
            cursor.execute("""
                    SELECT ordered_item, 
                        COUNT(*) AS total_ratings, 
                        ROUND(AVG(raiting_score), 2) AS avg_rating
                    FROM Order_raiting
                    where date BETWEEN DATE('now', '-30 days') AND DATE('now') 
                    GROUP BY ordered_item
                    ORDER BY avg_rating DESC, total_ratings DESC
                    limit 10
                ;
                """,)

            rows = cursor.fetchall()
            # print(rows)

            if rows:
                rating_text = f"```\n{top_lunch_listing_str}\n\n"
                for index, (item, count, avg_rating) in enumerate(rows, start=1):
                    rating_text += f"{index}. {item} ⭐ {avg_rating} ({count} votes)\n"
                rating_text += "```"

                await callback_query.message.edit_text(rating_text, reply_markup=main_menu_customer_keyboard, parse_mode="MarkdownV2")

            else:
                await callback_query.message.edit_text(
                    f"```\n{no_top_lunch_listing_str}\n```",
                    reply_markup=main_menu_customer_keyboard, parse_mode="MarkdownV2"
                )

    except sqlite3.Error as e:
        await callback_query.message.edit_text(f"```\n❌ Database error: {e}\n```", reply_markup=main_menu_customer_keyboard, parse_mode="MarkdownV2")
