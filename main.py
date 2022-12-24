import logging
import re
from pathlib import Path

from aiogram import Bot, types, md
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.utils.executor import start_webhook
from aiogram.utils.markdown import bold, text, italic
from aiogram.contrib.middlewares.i18n import I18nMiddleware
from aiogram.types import ParseMode, ContentType

from config import API_TOKEN, WEBHOOK_URL, WEBHOOK_PATH, WEBAPP_PORT, WEBAPP_HOST, I18N_DOMAIN
import CambridgeDictionaryAPI as cDict
import db
import keyboard as kb

logging.basicConfig(filename='logs/example.log', encoding='utf-8', level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

BASE_DIR = Path(__file__).parent
LOCALES_DIR = BASE_DIR / 'locales'

i18n = I18nMiddleware(I18N_DOMAIN, LOCALES_DIR)

dp.middleware.setup(i18n)
dp.middleware.setup(LoggingMiddleware())
# Alias for gettext method
_ = i18n.gettext


async def on_startup(dp):
    await bot.set_webhook(WEBHOOK_URL)
    # insert code here to run it after start


async def on_shutdown(dp):
    logging.warning('Shutting down..')

    # insert code here to run it before shutdown

    # Remove webhook (not acceptable in some cases)
    await bot.delete_webhook()

    # Close DB connection (if used)
    await dp.storage.close()
    await dp.storage.wait_closed()

    logging.warning('Bye!')


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.answer(_('Hello, {user}! Type /help').format(user=message.from_user.full_name),
                         reply_markup=kb.main_menu_kb)
    # "Hello! I'm Dictionary bot. Author - TheRealistic. use command /help"


@dp.message_handler(commands=['help'])
async def process_help_command(message: types.Message):
    msg = text(bold(_('I can answer on these commands:')),
               '/info', '/play', '/addword', '/note', '/settings', sep='\n')
    await message.reply(msg, parse_mode=ParseMode.MARKDOWN)


@dp.message_handler(commands=["play"])
async def play_game(message: types.Message):
    data = db.read_words(message.from_user.id)
    words = data.get(list(data.keys())[1])[0].get("word")
    meaning = data.get(list(data.keys())[1])[0].get("meaning")
    await message.reply("coming soon")


@dp.message_handler(commands=["addword"])
async def add_word(message: types.Message):
    message.text = message.text.replace('/addword', '')
    word = re.sub(".* ", '', message.text).lower()
    word_s = cDict.word_checker(word)
    print(word_s)
    if word_s == True:
        word_s = cDict.word_finder(word)
        db.add_word(word_s, message.from_user.id)
        await message.reply("Word: " + word + " was found and added successfully!")
    else:
        await message.reply("Your word is incorrect or doesn't exist in Cambridge Dictionary(HOW???)",
                            reply_markup=kb.generate_kb(word_s))


@dp.message_handler(commands=["show"])  # commands=["show"]
async def show_words(message: types.Message):
    data = db.read_words(message.from_user.id)
    res = ""
    for i in data:
        res += bold(i.get(list(i.keys())[1])[0].get("word"))
        res += ' - ' + italic(i.get(list(i.keys())[1])[0].get("meaning"))
        res += ";\n"
    print(res)
    await message.reply(res, parse_mode=ParseMode.MARKDOWN)


@dp.message_handler(commands=['info'])
async def info_user(message: types.Message):
    locale = message.from_user.locale

    await message.reply(md.text(
        md.bold('Info about your language:'),
        md.text('🔸', md.bold('Code:'), md.code(locale.language)),
        md.text('🔸', md.bold('Territory:'), md.code(locale.territory or 'Unknown')),
        md.text('🔸', md.bold('Language name:'), md.code(locale.language_name)),
        md.text('🔸', md.bold('English language name:'), md.code(locale.english_name)),
        sep='\n',
    ))


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('btn'))
async def process_callback_choice(callback_query: types.CallbackQuery):
    code = callback_query.data.replace('btn', '')
    word_s = cDict.word_finder(code)
    print(word_s)
    db.add_word(word_s, callback_query.from_user.id)
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, text="Word: " + code + " was added successfully")


@dp.message_handler(Text(equals="Add word"))
async def with_puree(message: types.Message):
    await message.reply("Enter the word:")


@dp.message_handler(content_types=ContentType.ANY)
async def unknown_message(message: types.Message):
    message_text = text('Я не знаю, что с этим делать',
                        '\nЯ просто напомню,', 'что есть', 'команда', '/help')
    await message.reply(message_text)


if __name__ == '__main__':
    start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        skip_updates=True,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT,
    )

# TODO:
#   Add additional information about word
#   Add DB(pony orm)
#   Add first setup
#   Add oauth2 - not important
#   Add localization
#   refactor the code
