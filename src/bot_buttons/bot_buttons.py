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

    current_bakekry_action = 'current_bakekry_action'
    edit_bakekry_action = 'edit_bakekry_action'
    current_lunch_menu_action = 'current_lunch_menu_action'
    edit_lunch_menu_action = 'edit_lunch_menu_action'



####################
customer_button = InlineKeyboardButton(
    text="I'm a customer", callback_data=StartCallbackData(action=Actions.CUSTOMER).pack())

administrator_button = InlineKeyboardButton(
    text="I'm an administrator", callback_data=StartCallbackData(action=Actions.administrator_action).pack())

start_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[[customer_button, administrator_button]])

main_menu_button = InlineKeyboardButton(
    text="Main menu", callback_data=StartCallbackData(action=Actions.return_main_menu_action).pack())

# CUSTOMERS options
order_lunch_btn = InlineKeyboardButton(
    text="Order a lunch", callback_data=StartCallbackData(action=Actions.order_lunch_action).pack())

order_bakery_btn = InlineKeyboardButton(
    text="Bakery", callback_data=StartCallbackData(action=Actions.order_bakery_action).pack())

specify_additions_btn = InlineKeyboardButton(
    text="Specify additions", callback_data=StartCallbackData(action=Actions.specify_additions_action).pack())

my_orders_btn = InlineKeyboardButton(
    text="My orders", callback_data=StartCallbackData(action=Actions.my_basket_action).pack())

lunch_rating_list_btn = InlineKeyboardButton(
    text="Lunch rating list", callback_data=StartCallbackData(action=Actions.lunch_rating_list_action).pack())

rate_your_lunch_btn = InlineKeyboardButton(
    text="Rate your lunch", callback_data=StartCallbackData(action=Actions.rate_your_lunch_action).pack())


leave_review_btn = InlineKeyboardButton(
    text="Leave a review", callback_data=StartCallbackData(action=Actions.leave_review_action).pack())


# New inline keyboard with multiple buttons
main_menu_customer_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [order_lunch_btn, order_bakery_btn],
    [specify_additions_btn],
    [my_orders_btn,],
    [lunch_rating_list_btn, rate_your_lunch_btn],
    [leave_review_btn,],
    [main_menu_button]
])

# # payment
# cash_payment_btn = InlineKeyboardButton(
#     text="Cash", callback_data='pay_cash')

# card_payment_btn = InlineKeyboardButton(
#     text="Card", callback_data='pay_card')


# payment_keyboard = InlineKeyboardMarkup(inline_keyboard=[
#     [cash_payment_btn, card_payment_btn],
#     [main_menu_button]
# ])



# ADMIN BUTTONS
current_lunch_menu_btn = InlineKeyboardButton(
    text="Current Lunch Menu", callback_data=StartCallbackData(action=Actions.current_lunch_menu_action).pack())
current_bakery_menu_btn = InlineKeyboardButton(
    text="Current Bakery Menu", callback_data=StartCallbackData(action=Actions.current_bakekry_action).pack())

reset_lunch_menu_btn = InlineKeyboardButton(
    text="Reset Lunch Menu", callback_data=StartCallbackData(action=Actions.edit_lunch_menu_action).pack())

reset_bakery_menu_btn = InlineKeyboardButton(
    text="Reset Bakery Menu", callback_data=StartCallbackData(action=Actions.edit_bakekry_action).pack())


main_menu_admin_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [current_lunch_menu_btn, current_bakery_menu_btn],
    [reset_lunch_menu_btn, reset_bakery_menu_btn],
    [main_menu_button]
])




