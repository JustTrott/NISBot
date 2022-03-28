from calendar import weekday
from filters import abort_factory, home_page_factory, parallel_page_factory, grade_page_factory, schedule_page_factory
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

def generate_home_keyboard(parallels: list[str]) -> None:
    keyboard = InlineKeyboardMarkup(row_width=3)
    keyboard.add(*[
        InlineKeyboardButton(
            text=parallel,
            callback_data=parallel_page_factory.new(parallel=parallel)
        )
        for parallel in parallels
    ])
    navigation_buttons = []
    navigation_buttons.append(
        InlineKeyboardButton(
            text='🗑', 
            callback_data=abort_factory.new()
        )
    )
    keyboard.add(*navigation_buttons)
    return keyboard

def generate_parallel_keyboard(parallel: str, letters: list[str]) -> None:
    keyboard = InlineKeyboardMarkup(row_width=3)
    keyboard.add(*[
        InlineKeyboardButton(
            text=parallel+letter,
            callback_data=grade_page_factory.new(parallel=parallel, letter=letter)
        )
        for letter in letters
    ])
    navigation_buttons = []
    navigation_buttons.append(
        InlineKeyboardButton(
            text='⬅️',
            callback_data=home_page_factory.new()
        )
    )
    navigation_buttons.append(
        InlineKeyboardButton(
            text='🗑', 
            callback_data=abort_factory.new()
        )
    )
    keyboard.add(*navigation_buttons)
    return keyboard

def generate_grade_keyboard(parallel: str, letter: str) -> None:
    weekdays = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница"]
    keyboard = InlineKeyboardMarkup(row_width=3)
    keyboard.add(
        InlineKeyboardButton(
            text='Выбрать автоматически',
            callback_data=schedule_page_factory.new(parallel=parallel, letter=letter, weekday='auto'))
    )
    keyboard.add(*[
        InlineKeyboardButton(
            text=weekday,
            callback_data=schedule_page_factory.new(parallel=parallel, letter=letter, weekday=weekday)
        )
        for weekday in weekdays
    ])
    navigation_buttons = []
    navigation_buttons.append(
        InlineKeyboardButton(
            text='⬅️',
            callback_data=parallel_page_factory.new(parallel=parallel)
        )
    )
    navigation_buttons.append(
        InlineKeyboardButton(
            text='🗑', 
            callback_data=abort_factory.new()
        )
    )
    keyboard.add(*navigation_buttons)
    return keyboard

def generate_schedule_keyboard(parallel: str, letter: str) -> None:
    keyboard = InlineKeyboardMarkup(row_width=3)
    navigation_buttons = []
    navigation_buttons.append(
        InlineKeyboardButton(
            text='⬅️',
            callback_data=grade_page_factory.new(parallel=parallel, letter=letter)
        )
    )
    navigation_buttons.append(
        InlineKeyboardButton(
            text='🗑', 
            callback_data=abort_factory.new()
        )
    )
    keyboard.add(*navigation_buttons)
    return keyboard
