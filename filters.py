import telebot
from telebot import types, AdvancedCustomFilter
from telebot.callback_data import CallbackData, CallbackDataFilter

abort_factory = CallbackData(prefix='abort')
home_page_factory = CallbackData(prefix='home_page')
parallel_page_factory = CallbackData('parallel', prefix='parallel_page')
grade_page_factory = CallbackData('parallel', 'letter', prefix='grade_page')
schedule_page_factory = CallbackData('parallel', 'letter', 'weekday', prefix='schedule_page') 


class AbortCallbackFilter(AdvancedCustomFilter):
    key = 'abort_config'

    def check(self, call: types.CallbackQuery, config: CallbackDataFilter):
        return config.check(query=call)


class HomePageCallbackFilter(AdvancedCustomFilter):
    key = 'home_page_config'

    def check(self, call: types.CallbackQuery, config: CallbackDataFilter):
        return config.check(query=call)


class ParallelPageCallbackFilter(AdvancedCustomFilter):
    key = 'parallel_page_config'

    def check(self, call: types.CallbackQuery, config: CallbackDataFilter):
        return config.check(query=call)


class GradePageCallbackFilter(AdvancedCustomFilter):
    key = 'grade_page_config'

    def check(self, call: types.CallbackQuery, config: CallbackDataFilter):
        return config.check(query=call)


class SchedulePageCallbackFilter(AdvancedCustomFilter):
    key = 'schedule_page_config'

    def check(self, call: types.CallbackQuery, config: CallbackDataFilter):
        return config.check(query=call)


def bind_filters(bot: telebot.TeleBot):
    bot.add_custom_filter(AbortCallbackFilter())
    bot.add_custom_filter(HomePageCallbackFilter())
    bot.add_custom_filter(ParallelPageCallbackFilter())
    bot.add_custom_filter(GradePageCallbackFilter())
    bot.add_custom_filter(SchedulePageCallbackFilter())