import sys
import telebot
from telebot import types
from config import Config
from sheet_parser import SpreadsheetParser
from time import sleep

cfg = Config()
if cfg.bot_token == '':
    print("Bot token is not found in config.ini")
    sys.exit()
weekdays = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница"]
sp = SpreadsheetParser('schedule.xlsx')
bot = telebot.TeleBot(cfg.bot_token)

@bot.message_handler(commands=['m'])
def send_msg(message):
    if message.from_user.id != 526419716:
        return
    chat_id = -1001252807888
    text = message.text[2:]#"@lulakebaber не кикай пж"
    bot.send_message(chat_id, text)


@bot.message_handler(commands=['schedule'])
def send_schedule(message):
    spy_string = f"/schedule command was used by {message.from_user.first_name}"
    spy_string += f" {message.from_user.last_name}" if message.from_user.last_name is not None else ""
    spy_string += f" with username @{message.from_user.username}" if message.from_user.username is not None else ""
    spy_string += f" in chat {message.chat.title}" if message.chat.title is not None else ""
    print(spy_string)
    markup = types.InlineKeyboardMarkup(row_width=3)
    parallels = [types.InlineKeyboardButton(item, callback_data=item) for item in cfg.classes]
    markup.add(*parallels)
    markup.add(types.InlineKeyboardButton("Отмена", callback_data='abort'))
    bot.send_message(message.chat.id, "Пожалуйста, выберите параллель:", reply_markup=markup, reply_to_message_id=message.message_id)

@bot.callback_query_handler(func=lambda call: True)
def handle(call):
    bot.answer_callback_query(call.id)
    if call.message.reply_to_message.from_user.id != call.from_user.id:
        return
    if call.data == 'abort':
            bot.delete_message(call.message.chat.id, call.message.message_id)
            try:
                bot.delete_message(call.message.chat.id, call.message.reply_to_message.message_id)
            except telebot.apihelper.ApiTelegramException:
                pass
            return
    if call.message.text == "Пожалуйста, выберите параллель:":
        markup = types.InlineKeyboardMarkup(row_width=3)
        parallel = call.data
        grades = [types.InlineKeyboardButton(parallel+grade, callback_data=parallel+grade) for grade in cfg.classes[parallel]]
        markup.add(*grades)
        markup.add(types.InlineKeyboardButton("Отмена", callback_data='abort'))
        bot.edit_message_text(f"Вы выбрали {parallel} параллель, выберите класс:",
            call.message.chat.id, call.message.message_id, reply_markup=markup)
        return
    if call.message.text.endswith("выберите класс:"):
        grade = call.data
        markup = types.InlineKeyboardMarkup(row_width=3)
        markup.add(*[types.InlineKeyboardButton(weekday, callback_data=f"{grade} {weekday}") for weekday in weekdays])
        markup.add(types.InlineKeyboardButton("Отмена", callback_data='abort'))
        bot.edit_message_text(f"Вы выбрали {grade} класс, выберите день недели:", call.message.chat.id, call.message.message_id, parse_mode='Markdown', reply_markup=markup)
        return
    if call.message.text.endswith("выберите день недели:"):
        print(f"{call.data = } by {call.from_user.first_name}")
        grade, weekday = call.data.split()
        sheet = sp.get_grade_schedule(grade, weekday)
        msgtext = f"""`{sheet}`"""
        markup = types.InlineKeyboardMarkup(row_width=3)
        markup.add(types.InlineKeyboardButton("Закрыть", callback_data='abort'))
        bot.edit_message_text(msgtext, call.message.chat.id, call.message.message_id, parse_mode='Markdown', reply_markup=markup)
        return

if __name__ == '__main__':
    print("Starting application...")
    bot.infinity_polling(skip_pending=True, interval=0)
