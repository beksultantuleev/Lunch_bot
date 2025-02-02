from core_bot.core_bot import *
from bot_buttons.bot_buttons import *
from aiogram.utils.markdown import bold
from aiogram.types import CallbackQuery
import sqlite3
import datetime



############################Comment
async def handle_review(callback_query: types.CallbackQuery, state: FSMContext):

    chat_id = callback_query.from_user.id
    user_languages.setdefault(chat_id, default_lang)
    selected_language = user_languages.get(chat_id, default_lang)
    type_review_str = get_translation("type_review_str", selected_language)
    
    await callback_query.message.edit_text(type_review_str)
    
    # Set state to waiting for the review
    await state.set_state(ReviewState.waiting_for_review)
    await callback_query.answer()


async def save_review(message: Message, state: FSMContext):
    current_date = datetime.datetime.now().strftime(date_mask)  # Current date in YYYY-MM-DD format
    review = message.text
    chat_id = message.chat.id
    username = message.chat.username

    

    user_languages.setdefault(chat_id, default_lang)
    selected_language = user_languages.get(chat_id, default_lang)
    main_menu_customer_keyboard = create_customer_menu_buttons(chat_id, user_languages)
    canceled_str = get_translation("canceled_str", selected_language)
    review_registered_str = get_translation("review_registered_str", selected_language)
    failed_review_registered_str = get_translation("failed_review_registered_str", selected_language)

    if message.text and message.text.lower() == "/start":
        await message.answer(canceled_str, reply_markup=main_menu_customer_keyboard)
        await state.clear()
        return

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
        await message.answer(review_registered_str, reply_markup=main_menu_customer_keyboard)
    except sqlite3.Error as e:
        await message.answer(f"{failed_review_registered_str}{e}", reply_markup=main_menu_customer_keyboard)

    # Clear the state
    await state.clear()

# Register the review handlers
dp.callback_query.register(handle_review, StateFilter(ReviewState.waiting_for_review))
dp.message.register(save_review, StateFilter(ReviewState.waiting_for_review))

############################