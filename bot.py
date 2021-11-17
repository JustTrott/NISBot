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
admin_id = cfg.admin_id

@bot.message_handler(commands=['m'])
def send_msg(message):
    if message.from_user.id != admin_id:
        return
    chat_id = -1001252807888
    text = message.text[2:]
    bot.send_message(chat_id, text)


@bot.message_handler(commands=['schedule'])
def send_schedule(message):
    spy_string = f"/schedule command was used by {message.from_user.first_name}"
    spy_string += f" {message.from_user.last_name}" if message.from_user.last_name is not None else ""
    spy_string += f" with username @{message.from_user.username}" if message.from_user.username is not None else ""
    spy_string += f" in chat {message.chat.title}" if message.chat.title is not None else ""
    print(spy_string)
    markup = types.InlineKeyboardMarkup(row_width=3)
    parallels = [types.InlineKeyboardButton(grade, callback_data="1 " + grade) for grade in cfg.classes]
    markup.add(*parallels)
    markup.add(types.InlineKeyboardButton("🗑", callback_data='abort'))
    bot.send_message(message.chat.id, "Пожалуйста, выберите параллель:", reply_markup=markup, reply_to_message_id=message.message_id)

@bot.callback_query_handler(func=lambda call: True)
def handle(call):
    bot.answer_callback_query(call.id)
    if call.message.reply_to_message.from_user.id != call.from_user.id and call.from_user.id != admin_id:
        return
    if call.data == 'abort':
            bot.delete_message(call.message.chat.id, call.message.message_id)
            try:
                bot.delete_message(call.message.chat.id, call.message.reply_to_message.message_id)
            except telebot.apihelper.ApiTelegramException:
                pass
            return
    call_type, call_data = call.data.split(' ', 1) #0 - page after issuing a command, 1 - first page, 2 - second page, 3 - third page of schedule

    if call_type == '0':
        markup = types.InlineKeyboardMarkup(row_width=3)
        parallels = [types.InlineKeyboardButton(grade, callback_data="1 " + grade) for grade in cfg.classes]
        markup.add(*parallels)
        markup.add(types.InlineKeyboardButton("🗑", callback_data='abort'))
        bot.edit_message_text("Пожалуйста, выберите параллель:", call.message.chat.id, call.message.message_id, reply_markup=markup)
        return

    if call_type == '1':
        markup = types.InlineKeyboardMarkup(row_width=3)
        parallel = call_data
        grades = [types.InlineKeyboardButton(parallel+letter, callback_data='2 ' + f"{parallel} {letter}") for letter in cfg.classes[parallel]]
        markup.add(*grades)
        navigation_buttons = []
        navigation_buttons.append(types.InlineKeyboardButton("⬅️", callback_data='0 ' + 'None'))
        navigation_buttons.append(types.InlineKeyboardButton("🗑", callback_data='abort'))
        markup.add(*navigation_buttons)
        bot.edit_message_text(f"Вы выбрали {parallel} параллель, выберите класс:",
            call.message.chat.id, call.message.message_id, reply_markup=markup)
        return

    if call_type == '2':
        parallel, letter = call_data.split()
        markup = types.InlineKeyboardMarkup(row_width=3)
        markup.add(types.InlineKeyboardButton("Выбрать автоматически", callback_data='3 ' + f"{parallel} {letter} auto"))
        markup.add(*[types.InlineKeyboardButton(weekday, callback_data='3 ' + f"{parallel} {letter} {weekday}") for weekday in weekdays])
        navigation_buttons = []
        navigation_buttons.append(types.InlineKeyboardButton("⬅️", callback_data='1 ' + parallel))
        navigation_buttons.append(types.InlineKeyboardButton("🗑", callback_data='abort'))
        markup.add(*navigation_buttons)
        bot.edit_message_text(f"Вы выбрали {parallel}{letter} класс, выберите день недели:", call.message.chat.id, call.message.message_id, parse_mode='Markdown', reply_markup=markup)
        return

    if call_type == '3':
        print(f"{call_data = } by {call.from_user.first_name}")
        parallel, letter, weekday = call_data.split()
        sheet = sp.get_grade_schedule(parallel+letter, weekday)
        msgtext = f"""`{sheet}`"""
        markup = types.InlineKeyboardMarkup(row_width=3)
        navigation_buttons = []
        navigation_buttons.append(types.InlineKeyboardButton("⬅️", callback_data='2 ' +  f"{parallel} {letter}"))
        navigation_buttons.append(types.InlineKeyboardButton("🗑", callback_data='abort'))
        markup.add(*navigation_buttons)
        bot.edit_message_text(msgtext, call.message.chat.id, call.message.message_id, parse_mode='Markdown', reply_markup=markup)
        return

if __name__ == '__main__':
    print("Starting application...")
    bot.infinity_polling(skip_pending=True, interval=0)
