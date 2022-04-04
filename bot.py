import sys
from uuid import uuid4

import telebot
from telebot import types

from config import Config
from sheet_parser import SpreadsheetParser
from filters import abort_factory, home_page_factory, parallel_page_factory, grade_page_factory, schedule_page_factory, bind_filters
from keyboards import generate_home_keyboard, generate_parallel_keyboard, generate_grade_keyboard, generate_schedule_keyboard

cfg = Config()
if cfg.bot_token == '':
    print("Bot token is not found in config.ini")
    sys.exit()
sp = SpreadsheetParser('schedule.xlsx')
bot = telebot.TeleBot(cfg.bot_token)
def_msg = "Бот так ошалел от нового расписания, что не выдержал и уше́л на технические работы. Приносим наши извинения."


@bot.message_handler(commands=['m'])
def send_msg(message : types.Message):
    if message.from_user.id != cfg.admin_id:
        return
    chat_id = -1001252807888
    text = message.text[2:]
    bot.send_message(chat_id, text)


@bot.message_handler(commands=['start'])
def send_welcome(message: types.Message):
    welcome_message = "Этот бот позволяет вам *быстро* получить школьное расписание НИШ ФМН в городе Нур-Султан, включая информацию о **кабинетах** и **времени** проведения уроков."
    welcome_message += "\nПросто напишите /schedule и следуйте инструкциям! <- Команда также работает и в *группах*"
    welcome_message += "\nТакже можно вызвать бота не добавляя его, в любом чате, написав @TrottTheBot"
    welcome_message += "\nСпасибо, что пользуетесь ботом. Автор: @TrottTheDev"
    bot.send_message(message.chat.id, welcome_message, parse_mode="Markdown")


@bot.message_handler(commands=['schedule'])
def send_schedule(message : types.Message):
    bot.send_message(message.chat.id, def_msg)
    return
    spy_string = f"/schedule command was used by {message.from_user.first_name}"
    spy_string += f" {message.from_user.last_name}" if message.from_user.last_name is not None else ""
    spy_string += f" with username @{message.from_user.username}" if message.from_user.username is not None else ""
    spy_string += f" in chat {message.chat.title}" if message.chat.title is not None else ""
    print(spy_string)
    bot.send_message(message.chat.id, "Пожалуйста, выберите параллель:", reply_markup=generate_home_keyboard(list(cfg.classes.keys())), reply_to_message_id=message.message_id)


@bot.callback_query_handler(func=None, abort_config=abort_factory.filter())
def abort(call : types.CallbackQuery):
    return
    bot.answer_callback_query(call.id, "Запрос был удалён.")
    bot.delete_message(call.message.chat.id, call.message.id)
    try:
        bot.delete_message(call.message.chat.id, call.message.reply_to_message.message_id)
    except telebot.apihelper.ApiTelegramException:
        pass


@bot.callback_query_handler(func=None, home_page_config=home_page_factory.filter())
def send_home_page(call: types.CallbackQuery):
    return
    bot.edit_message_text("Пожалуйста, выберите параллель:", call.message.chat.id, call.message.message_id, 
        reply_markup=generate_home_keyboard(list(cfg.classes.keys())))
    bot.answer_callback_query(call.id, "Вы были возвращены на страницу выбора параллелей.")


@bot.callback_query_handler(func=None, parallel_page_config=parallel_page_factory.filter())
def send_parallel_page(call: types.CallbackQuery):
    return
    callback_data: dict[str, str] = parallel_page_factory.parse(callback_data=call.data)
    parallel = callback_data['parallel']
    bot.edit_message_text(f"Вы выбрали {parallel} параллель, выберите класс:", call.message.chat.id, call.message.message_id, 
        reply_markup=generate_parallel_keyboard(parallel, [letter for letter in cfg.classes[parallel]]))
    bot.answer_callback_query(call.id, f"{parallel} параллель была выбрана успешно.")


@bot.callback_query_handler(func=None, grade_page_config=grade_page_factory.filter())
def send_grade_page(call: types.CallbackQuery):
    return
    callback_data: dict[str, str] = grade_page_factory.parse(callback_data=call.data)
    parallel, letter = callback_data['parallel'], callback_data['letter']    
    bot.edit_message_text(f"Вы выбрали {parallel}{letter} класс, выберите день недели:", call.message.chat.id, call.message.message_id, parse_mode='Markdown', 
        reply_markup=generate_grade_keyboard(parallel=parallel, letter=letter))
    bot.answer_callback_query(call.id, f"{parallel}{letter} класс был выбран успешно.")


@bot.callback_query_handler(func=None, schedule_page_config=schedule_page_factory.filter())
def send_schedule_page(call: types.CallbackQuery):
    return
    callback_data: dict[str, str] = schedule_page_factory.parse(callback_data=call.data)
    parallel, letter, weekday = callback_data['parallel'], callback_data['letter'], callback_data['weekday']
    print(f'{parallel}{letter} Grade for {weekday} schedule was requested by {call.from_user.first_name}')
    sheet = sp.get_grade_schedule(parallel+letter, weekday)
    text = f"""`{sheet}`"""
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode='Markdown',
        reply_markup=generate_schedule_keyboard(parallel=parallel, letter=letter))
    bot.answer_callback_query(call.id)


def is_query_a_grade(query: str) -> bool:
    return False
    query = query.strip()
    if query == '':
        return False
    grades = cfg.classes
    for parallel in grades:
        for letter in grades[parallel]:
            if query.upper() in str(parallel + letter) or str(parallel + letter) in query.upper():
                return True
    return False


@bot.inline_handler(lambda query: is_query_a_grade(query.query))
def show_grades(inline_query: types.InlineQuery):
    grades = cfg.classes
    possible_grades = []
    for parallel in grades:
        for letter in grades[parallel]:
            grade = parallel + letter
            if inline_query.query.upper() in grade or grade in inline_query.query.upper():
                possible_grades.append(grade)
    responses = [
        types.InlineQueryResultArticle(
            id=str(uuid4()),
            title=possible_grades[i],
            input_message_content=types.InputTextMessageContent(f"""`{sheet}`""", parse_mode='Markdown'),
            description=sp.get_current_weekday()
        )
        for i, sheet in enumerate(sp.get_grade_schedule_bulk(possible_grades, 'auto'))
    ]
    bot.answer_inline_query(inline_query.id, responses, cache_time=5)


if __name__ == '__main__':
    print("Starting application...")
    bind_filters(bot)
    bot.infinity_polling(skip_pending=True, interval=0)
