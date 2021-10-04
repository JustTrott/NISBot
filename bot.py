import sys
import telebot
from telebot import types
from config import Config
from spreadsheetParser import SpreadsheetParser
from time import sleep
import threading

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
    markup.add(types.InlineKeyboardButton("Отмена", callback_data='abort'))
    bot.send_message(message.chat.id, "Пожалуйста, выберите параллель:", reply_markup=markup, reply_to_message_id=message.message_id)

@bot.message_handler()
def hide_keyboard(message):
    if message.text != "hide":
        return
    markup = types.ReplyKeyboardRemove(selective=False)
    bot.send_message(message.chat.id, 'hidden!', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def handle(call):
    if call.data == 'abort' and call.message.reply_to_message.from_user.id == call.from_user.id:
            bot.delete_message(call.message.chat.id, call.message.message_id)
            try:
                bot.delete_message(call.message.chat.id, call.message.reply_to_message.message_id)
            except telebot.apihelper.ApiTelegramException:
                message = bot.reply_to(call.message.reply_to_message, "Недостаточно прав чтобы удалить это сообщение.\n`Это сообщение, будет удалено через 5 секунд`", parse_mode="Markdown")
                t = threading.Thread(target=delayed_message_deletion(message))
                t.start()
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
        sp = SpreadsheetParser(grade)
        msgtext = f"""`{sp.sheet}`"""
        markup = types.InlineKeyboardMarkup(row_width=3)
        markup.add(types.InlineKeyboardButton("Закрыть", callback_data='abort'))
        bot.edit_message_text(msgtext, call.message.chat.id, call.message.message_id, parse_mode='Markdown', reply_markup=markup)
        return
    bot.answer_callback_query(call.id)

def delayed_message_deletion(message):
    sleep(5)
    bot.delete_message(message.chat.id, message.message_id)

if __name__ == '__main__':
    print("Starting application...")
    bot.infinity_polling(skip_pending=True, interval=0)
