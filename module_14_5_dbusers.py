#name - KanBot
#user - KanTrainingBot
#API token - 7898382293:AAHPegX5CCa6JJP_kojyMd2DdWOWYnZSKWQ

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio
import crud_functions

api = '7898382293:AAHPegX5CCa6JJP_kojyMd2DdWOWYnZSKWQ'
bot = Bot(api)
dp = Dispatcher(bot, storage=MemoryStorage())

class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()

class RegistrationState(StatesGroup):
    username = State()
    email = State()
    age = State()
    balance = 1000

kb = ReplyKeyboardMarkup(resize_keyboard = True, input_field_placeholder = "Выберите действие")
button_calc = KeyboardButton(text = 'Рассчитать')
button_info = KeyboardButton(text = 'Информация')
button_bye = KeyboardButton(text = 'Купить')
button_reg = KeyboardButton(text = 'Регистрация')
kb.row(button_calc, button_info, button_bye, button_reg)

inline_kb = InlineKeyboardMarkup(resize_keyboard = True)
inline_button_calories = InlineKeyboardButton(text = 'Рассчитать норму калорий', callback_data = 'calories')
inline_button_formulas = InlineKeyboardButton(text = 'Формулы расчета', callback_data = 'formulas')
inline_kb.row(inline_button_calories, inline_button_formulas)

inline_kb_bye = InlineKeyboardMarkup(resize_keyboard = True)
inline_button_1 = InlineKeyboardButton(text = 'Product1', callback_data = 'product_buying')
inline_button_2 = InlineKeyboardButton(text = 'Product2', callback_data = 'product_buying')
inline_button_3 = InlineKeyboardButton(text = 'Product3', callback_data = 'product_buying')
inline_button_4 = InlineKeyboardButton(text = 'Product4', callback_data = 'product_buying')
inline_kb_bye.row(inline_button_1, inline_button_2, inline_button_3, inline_button_4)

crud_functions.initiate_db()
products = crud_functions.get_all_products()

@dp.message_handler(text = ['Рассчитать'])
async def main_menu(message):
    await message.answer('Выберите опцию', reply_markup = inline_kb)

@dp.callback_query_handler(text = 'formulas')
async def get_formulas(call):
    await call.message.answer('вес * 10 + рост * 6.25 - возраст * 5 + 5')

@dp.callback_query_handler(text = 'calories')
async def set_age(call):
    await call.message.answer('Введите свой возраст')
    await UserState.age.set()

@dp.message_handler(text = ['Регистрация'])
async def sign_up(message):
    await message.answer('Введите имя пользователя (только латинский алфавит):')
    await RegistrationState.username.set()

@dp.message_handler(state = RegistrationState.username)
async def set_username(message, state):
    if not crud_functions.is_include(message.text):
        await state.update_data(username = message.text)
        await message.answer('Введите свой email:')
        await RegistrationState.email.set()
    else:
        await message.answer('Пользователь существует, введите другое имя')
        await RegistrationState.username.set()

@dp.message_handler(state = RegistrationState.email)
async def set_email(message, state):
    await state.update_data(email=message.text)
    await message.answer('Введите свой возраст')
    await RegistrationState.age.set()

@dp.message_handler(state = RegistrationState.age)
async def set_age(message, state):
    await state.update_data(age=message.text)
    user_data = await state.get_data()
    crud_functions.add_user(user_data['username'], user_data['email'], user_data['age'])
    await message.answer(f"Регистрация пользователя {user_data['username']} прошла успешно")
    await state.finish()

@dp.message_handler(text = ['Информация'])
async def info(message):
    await message.answer('Привет! Я могу рассчитать суточную норму калорий ')

@dp.message_handler(text = ['Купить'])
async def get_buying_list(message):
    for product in products:
        await message.answer(f'Название: {product[1]} | Описание: {product[2]} | Цена: {product[3]}')
        with open(f'files/Картинка {product[0]}.jpg', 'rb') as img:
            await message.answer_photo(img)
    await message.answer('Выберите продукт для покупки', reply_markup = inline_kb_bye)

@dp.callback_query_handler(text = 'product_buying')
async def send_confirm_message(call):
    await call.message.answer('Вы успешно приобрели продукт!')

@dp.message_handler(state = UserState.age)
async def set_growth(message, state):
    await state.update_data(age = message.text)
    await message.answer('Введите свой рост')
    await UserState.growth.set()

@dp.message_handler(state = UserState.growth)
async def set_weight(message, state):
    await state.update_data(growth = message.text)
    await message.answer('Введите свой вес')
    await UserState.weight.set()

@dp.message_handler(state = UserState.weight)
async def send_calories(message, state):
    await state.update_data(weight = message.text)
    data = await state.get_data()
    norma = int(data['weight']) * 10 + int(data['growth']) * 6.25 - int(data['age']) * 5 + 5
    await message.answer(f'Ваша норма калорий {norma}')
    await state.finish()

@dp.message_handler(commands = ['start'])
async def start(message):
    await message.answer('Привет! Я бот помогающий твоему здоровью.',
                         reply_markup = kb)

@dp.message_handler()
async def all_message(message):
    await message.answer('Введите команду /start, чтобы начать общение.')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

crud_functions.connection.close()