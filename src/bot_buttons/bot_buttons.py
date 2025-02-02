from core_bot.core_bot import *
from callback_data.callback_logic import *


class Actions:

    CUSTOMER = "customer_action"
    ADMIN = "administrator_action"

    # customer_action = 'customer_menu'
    return_main_menu_action = 'main_menu'

    order_lunch_action = 'order_lunch_action'
    order_bakery_action = 'order_bakery_action'
    specify_additions_action = 'specify_additions_action'
    my_basket_action = 'my_orders_action'
    leave_review_action = 'leave_review_action'
    leave_comment_action = 'leave_comment_action'
    lunch_rating_list_action = 'lunch_rating_list_action'
    rate_your_lunch_action = 'rate_your_lunch_action'
    administrator_action = 'administrator_action'
    export_today_excel_action = 'export_today_excel_action'
    export_all_excel_action = 'export_all_excel_action'
    export_review_excel_action = 'export_review_excel_action'
    export_review_wc_action = 'export_review_wc_action'

    # current_bakekry_action = 'current_bakekry_action'
    # edit_bakekry_action = 'edit_bakekry_action'
    current_lunch_menu_action = 'current_lunch_menu_action'
    current_lunch_menu_c_action = 'current_lunch_menu_c_action'
    edit_lunch_menu_action = 'edit_lunch_menu_action'



def create_initial_buttons(chat_id: int, user_languages: dict) -> InlineKeyboardMarkup:
    user_languages.setdefault(chat_id, default_lang)
    selected_language = user_languages.get(chat_id, default_lang)

    # Translate button texts
    im_a_customer_str = get_translation("im_a_cutomer_str", selected_language)
    im_admin_str = get_translation("im_admin_str", selected_language)

    customer_button = InlineKeyboardButton(
    text=im_a_customer_str, callback_data=StartCallbackData(action=Actions.CUSTOMER).pack())

    administrator_button = InlineKeyboardButton(
        text=im_admin_str, callback_data=StartCallbackData(action=Actions.administrator_action).pack())

    start_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [customer_button,],
            [administrator_button],
                         ])
    
    return start_keyboard


def create_customer_menu_buttons(chat_id: int, user_languages: dict) -> InlineKeyboardMarkup:
    user_languages.setdefault(chat_id, default_lang)
    selected_language = user_languages.get(chat_id, default_lang)
    main_menu_str = get_translation("main_menu_str", selected_language)
    order_lunch_str = get_translation("order_lunch_str", selected_language)
    garnish_str = get_translation("garnish_str", selected_language)
    my_orders_str = get_translation("my_orders_str", selected_language)
    lunch_rating_list_str = get_translation("lunch_rating_list_str", selected_language)
    rate_lunch_str = get_translation("rate_lunch_str", selected_language)
    leave_review_str = get_translation("leave_review_str", selected_language)
    current_lunch_menu_str = get_translation("current_lunch_menu_str", selected_language)
    word_cloud_btn_str = get_translation("word_cloud_btn_str", selected_language)

    main_menu_button = InlineKeyboardButton(
        text=main_menu_str, callback_data=StartCallbackData(action=Actions.return_main_menu_action).pack())
    # CUSTOMERS options
    order_lunch_btn = InlineKeyboardButton(
        text=order_lunch_str, callback_data=StartCallbackData(action=Actions.order_lunch_action).pack())

    # order_bakery_btn = InlineKeyboardButton(
    #     text="Bakery", callback_data=StartCallbackData(action=Actions.order_bakery_action).pack())

    specify_additions_btn = InlineKeyboardButton(
        text=garnish_str, callback_data=StartCallbackData(action=Actions.specify_additions_action).pack())

    my_orders_btn = InlineKeyboardButton(
        text=my_orders_str, callback_data=StartCallbackData(action=Actions.my_basket_action).pack())

    lunch_rating_list_btn = InlineKeyboardButton(
        text=lunch_rating_list_str, callback_data=StartCallbackData(action=Actions.lunch_rating_list_action).pack())

    rate_your_lunch_btn = InlineKeyboardButton(
        text=rate_lunch_str, callback_data=StartCallbackData(action=Actions.rate_your_lunch_action).pack())


    leave_review_btn = InlineKeyboardButton(
        text=leave_review_str, callback_data=StartCallbackData(action=Actions.leave_review_action).pack())
    
    word_cloud_review_btn = InlineKeyboardButton(
        text=word_cloud_btn_str, callback_data=StartCallbackData(action=Actions.export_review_wc_action).pack())

    current_lunch_menu_c_btn = InlineKeyboardButton(
        text=current_lunch_menu_str, callback_data=StartCallbackData(action=Actions.current_lunch_menu_c_action).pack())

    # New inline keyboard with multiple buttons
    main_menu_customer_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [current_lunch_menu_c_btn],
        [order_lunch_btn, specify_additions_btn],
        # [specify_additions_btn],
        [my_orders_btn,],
        [lunch_rating_list_btn,rate_your_lunch_btn],
        # [rate_your_lunch_btn],
        [leave_review_btn, word_cloud_review_btn,],
        # [word_cloud_review_btn,],
        [main_menu_button]
    ])
    return main_menu_customer_keyboard


def create_admin_menu_buttons(chat_id: int, user_languages: dict) -> InlineKeyboardMarkup:
    user_languages.setdefault(chat_id, default_lang)
    selected_language = user_languages.get(chat_id, default_lang)
    
    reset_lunch_menu_str = get_translation("reset_lunch_menu_str", selected_language)
    current_lunch_menu_str = get_translation("current_lunch_menu_str", selected_language)
    export_today_data_str = get_translation("export_today_data_str", selected_language)
    export_all_data_str = get_translation("export_all_data_str", selected_language) 
    main_menu_str = get_translation("main_menu_str", selected_language)
    export_review_btn_str = get_translation("export_review_btn_str", selected_language)


    reset_lunch_menu_btn = InlineKeyboardButton(
    text=reset_lunch_menu_str, callback_data=StartCallbackData(action=Actions.edit_lunch_menu_action).pack())

    current_lunch_menu_btn = InlineKeyboardButton(
        text=current_lunch_menu_str, callback_data=StartCallbackData(action=Actions.current_lunch_menu_action).pack())

    export_today_excel_btn = InlineKeyboardButton(
        text=export_today_data_str, callback_data=StartCallbackData(action=Actions.export_today_excel_action).pack())

    export_all_excel_btn = InlineKeyboardButton(
        text=export_all_data_str, callback_data=StartCallbackData(action=Actions.export_all_excel_action).pack())
    
    export_all_review_btn = InlineKeyboardButton(
        text=export_review_btn_str, callback_data=StartCallbackData(action=Actions.export_review_excel_action).pack())
    
    main_menu_button = InlineKeyboardButton(
        text=main_menu_str, callback_data=StartCallbackData(action=Actions.return_main_menu_action).pack())

    main_menu_admin_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        # [current_lunch_menu_btn, current_bakery_menu_btn],
        [current_lunch_menu_btn,],
        # [reset_lunch_menu_btn, reset_bakery_menu_btn],
        [reset_lunch_menu_btn,],
        [export_today_excel_btn, export_all_excel_btn],
        [export_all_review_btn],
        [main_menu_button],
    ])
    return main_menu_admin_keyboard

