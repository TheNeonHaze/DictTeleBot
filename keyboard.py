from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton


def generate_kb(data):
    btn_arr = InlineKeyboardMarkup()
    for i in data[0]:
        btn_arr.add(InlineKeyboardButton(i, callback_data='btn' + i))
    return btn_arr


button_hi = KeyboardButton('Привет! 👋')

greet_kb = ReplyKeyboardMarkup()
greet_kb.add(button_hi)


button_add_word = KeyboardButton('Add word')
button_show_list_of_words = KeyboardButton('Show words')
button_settings = KeyboardButton('Settings')

main_menu_kb = ReplyKeyboardMarkup(one_time_keyboard=True).add(button_add_word)\
    .add(button_show_list_of_words).add(button_settings)  # resize_keyboard=True
