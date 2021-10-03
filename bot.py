import sys
import telebot
from telebot import types
from config import Config
from spreadsheetParser import SpreadsheetParser

cfg = Config()
if cfg.bot_token == '':
    print("Bot token is not found in config.ini")
    sys.exit()
bot = telebot.TeleBot(cfg.bot_token)
@bot.message_handler(commands=['schedule'])
def send_schedule(message):
    markup = types.InlineKeyboardMarkup(row_width=3)
    parallels = [types.InlineKeyboardButton(item, callback_data=item) for item in cfg.classes]
    markup.add(*parallels)
    bot.send_message(message.chat.id, "Пожалуйста, выберите параллель:", reply_markup=markup, reply_to_message_id=message.message_id)

@bot.message_handler()
def hide_keyboard(message):
    if message.text != "hide":
        return
    markup = types.ReplyKeyboardRemove(selective=False)
    bot.send_message(message.chat.id, 'hidden!', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def handle(call):
    if call.message.text == "Пожалуйста, выберите параллель:":
        markup = types.InlineKeyboardMarkup(row_width=3)
        parallel = call.data
        grades = [types.InlineKeyboardButton(parallel+grade, callback_data=parallel+grade) for grade in cfg.classes[parallel]]
        markup.add(*grades)
        bot.send_message(call.message.chat.id, f"Вы выбрали {parallel} параллель, выберите класс:", reply_markup=markup)
        bot.delete_message(call.message.chat.id, call.message.message_id)
    elif call.message.text.endswith("выберите класс:"):
        grade = call.data
        sp = SpreadsheetParser(grade)
        msgtext = f"""`{sp.sheet}`"""
        bot.send_message(call.message.chat.id, msgtext, parse_mode='Markdown')
        bot.delete_message(call.message.chat.id, call.message.message_id)
        #schedule_photo = ScheduleParser.get_schedule(grade)
        #bot.send_photo(call.message.chat.id, schedule_photo, f"Расписание {grade} класса:")

    bot.answer_callback_query(call.id)


if __name__ == '__main__':
    print("Starting application...")
    bot.infinity_polling(skip_pending=True, interval=0)
