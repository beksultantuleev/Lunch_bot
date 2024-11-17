from aiogram.filters.callback_data import CallbackData

# Define callback data structure with an action
class StartCallbackData(CallbackData, prefix="start"):
    action: str

# # Define callback data structure with an action
# class HelpCallbackData(CallbackData, prefix="help"):
#     action: str