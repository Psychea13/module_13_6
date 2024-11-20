from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio

api = 'top secret'
bot = Bot(token=api)
dp = Dispatcher(bot, storage=MemoryStorage())

kb = ReplyKeyboardMarkup(resize_keyboard=True)
button_1 = KeyboardButton(text='Рассчитать')
button_2 = KeyboardButton(text='Информация')
kb.row(button_1, button_2)

kb1 = InlineKeyboardMarkup()
button_3 = InlineKeyboardButton(text='Рассчитать норму калорий', callback_data='calories')
button_4 = InlineKeyboardButton(text='Формулы расчёта', callback_data='formulas')
kb1.row(button_3, button_4)


class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()
    sex = State()


@dp.message_handler(text='Рассчитать')
async def main_menu(message):
    await message.answer('Выберите опцию:', reply_markup=kb1)


@dp.callback_query_handler(text='formulas')
async def get_formulas(call):
    await call.message.answer('Формула Миффлина-Сан Жеора:\n'
                              '- для мужчин: 10 х вес (кг) + 6,25 x рост (см) – 5 х возраст (г) + 5;\n'
                              '- для женщин: 10 x вес (кг) + 6,25 x рост (см) – 5 x возраст (г) – 161.')
    await call.answer()


@dp.callback_query_handler(text='calories')
async def set_sex(call):
    await call.message.answer('Введите свой пол (м/ж):')
    await UserState.sex.set()


@dp.message_handler(state=UserState.sex)
async def set_age(message, state):
    await state.update_data(sex=message.text)
    await message.answer('Введите свой возраст:')
    await UserState.age.set()


@dp.message_handler(state=UserState.age)
async def set_growth(message, state):
    await state.update_data(age=message.text)
    await message.answer('Введите свой рост (см):')
    await UserState.growth.set()


@dp.message_handler(state=UserState.growth)
async def set_weight(message, state):
    await state.update_data(growth=message.text)
    await message.answer('Введите свой вес (кг):')
    await UserState.weight.set()


@dp.message_handler(state=UserState.weight)
async def send_calories(message, state):
    await state.update_data(weight=message.text)
    data = await state.get_data()
    if data['sex'] == 'ж':
        calorie_norm = 10 * float(data['weight']) + 6.25 * float(data['growth']) - 5 * float(data['age']) - 161
        await message.answer(f'Ваша норма - {calorie_norm} калорий в сутки')
    elif data['sex'] == 'м':
        calorie_norm = 10 * float(data['weight']) + 6.25 * float(data['growth']) - 5 * float(data['age']) + 5
        await message.answer(f'Ваша норма - {calorie_norm} калорий в сутки')
    else:
        await message.answer('Данные введены неверно. Попробуйте снова.')
    await state.finish()


@dp.message_handler(commands=['start'])
async def start(message):
    await message.answer('Привет! Я бот помогающий твоему здоровью.', reply_markup=kb)


@dp.message_handler(text='Информация')
async def inform(message):
    await message.answer('Этот бот умеет рассчитывать калории для оптимального похудения или сохранения '
                         'нормального веса по формуле Миффлина-Сан Жеора.')


@dp.message_handler()
async def all_message(message):
    await message.answer('Введите команду /start, чтобы начать общение.')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
