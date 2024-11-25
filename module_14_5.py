import os.path
import re

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio

from crud_functions import *

api = ''
bot = Bot(token=api)
dp = Dispatcher(bot, storage=MemoryStorage())

kb = ReplyKeyboardMarkup(resize_keyboard=True)
button = KeyboardButton(text='Рассчитать')
button2 = KeyboardButton(text='Информация')
button3 = KeyboardButton(text='Купить')
button4 = KeyboardButton(text='Регистрация')
kb.row(button, button2)
kb.row(button3, button4)

kb2 = InlineKeyboardMarkup(resize_keyboard=True)
in_line_button = InlineKeyboardButton(text='Рассчитать норму калорий', callback_data='calories')
in_line_button2 = InlineKeyboardButton(text='Формулы расчета', callback_data='formulas')
kb2.add(in_line_button)
kb2.add(in_line_button2)

inline_menu = InlineKeyboardMarkup(row_width=4)
product1 = InlineKeyboardButton(text='Продукт 1', callback_data='product_buying')
product2 = InlineKeyboardButton(text='Продукт 2', callback_data='product_buying')
product3 = InlineKeyboardButton(text='Продукт 3', callback_data='product_buying')
product4 = InlineKeyboardButton(text='Продукт 4', callback_data='product_buying')
inline_menu.add(product1, product2, product3, product4)


class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()


class RegistrationState(StatesGroup):
    username = State()
    email = State()
    age = State()
    balance = 1000


@dp.message_handler(text='Рассчитать')
async def main_menu(message):
    await message.answer('Выбирете опцию', reply_markup=kb2)


@dp.callback_query_handler(text='formulas')
async def get_formulas(call):
    await call.message.answer('(10 × вес в кг) + (6,25 × рост в см) − (5 × возраст в годах) + 5')
    await call.answer()


@dp.message_handler(commands=['start'])
async def start(message):
    initiate_db()
    await message.answer('Выбирете действие', reply_markup=kb)


@dp.message_handler(text='Информация')
async def inform(message):
    await message.answer('Для рассчета калорий нажмите на "Рассчитать"')


@dp.callback_query_handler(text='calories')
async def set_age(call):
    await call.message.answer('Введите свой возраст')
    await call.answer()
    await UserState.age.set()


@dp.message_handler(state=UserState.age)
async def set_growth(message, state):
    await state.update_data(age=message.text)
    await message.answer('Введите свой рост')
    await UserState.growth.set()


@dp.message_handler(state=UserState.growth)
async def set_weight(message, state):
    await state.update_data(growth=message.text)
    await message.answer('Введите свой вес')
    await UserState.weight.set()


@dp.message_handler(state=UserState.weight)
async def send_calories(message, state):
    await state.update_data(weight=message.text)
    data = await state.get_data()
    age = float(data['age'])
    growth = float(data['growth'])
    weight = float(data['weight'])

    fms = 10 * weight + 6.25 * growth - 5 * age + 5
    calories = fms * 1.2

    await message.answer(calories)
    await state.finish()


@dp.message_handler(text='Купить')
async def get_buying_list(message):
    products = get_all_products()
    if not products:
        await message.answer('В базе данных пока нет продуктов')
        return
    for product in products:
        product_id, title, description, price, image_path = product
        try:
            if not os.path.exists(image_path):
                raise FileNotFoundError(f'Файл {image_path} не найден')

            with open(image_path, 'rb') as img:
                await message.answer_photo(img, f'Название: {title} | Описание: {description} | Цена: {price}')
        except FileNotFoundError as e:
            await message.answer(f'Ошибка: Изображение для продукта "{title}" не найдено')
            print(e)
        except Exception as e:
            await message.answer(f'Произошла ошибка при обработке продукта "{title}".')
            print(f"Неизвестная ошибка для продукта {title}: {e}")
    await message.answer('Выберете продукт для покупки:', reply_markup=inline_menu)


@dp.callback_query_handler(text='product_buying')
async def send_confirm_message(call):
    await call.message.answer('Вы успешно приобрели продукт!')
    await call.answer()


@dp.message_handler(text='Регистрация')
async def sign_up(message):
    await message.answer('Введите имя пользователя (только латинский алфавит):')
    await RegistrationState.username.set()


@dp.message_handler(state=RegistrationState.username)
async def set_username(message, state):
    username = message.text
    if not re.match(r'[a-zA-Z]+$', username):
        await message.answer('Имя пользователя должно содержать только латинские буквы. Попробуйте снова.')
        return
    if not is_included(username):
        await state.update_data(username=username)
        await message.answer('Введите свой email:')
        await RegistrationState.email.set()
    else:
        await message.answer('Пользователь существует, введите другое имя')
        await RegistrationState.username.set()


@dp.message_handler(state=RegistrationState.email)
async def set_email(message, state):
    email = message.text
    if not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email):
        await message.answer('Некорректный формат email. Попробуйте снова.')
        return
    await state.update_data(email=email)
    await message.answer('Введите свой возраст:')
    await RegistrationState.age.set()


@dp.message_handler(state=RegistrationState.age)
async def set_age(message, state):
    age = message.text
    if not age.isdigit() or int(age) <= 0:
        await message.answer('Возраст должен быть положительным числом. Попробуйте снова.')
        return
    await state.update_data(age=age)
    data = await state.get_data()
    add_user(data['username'], data['email'], data['age'])
    await message.answer('Регистрация завершена!')
    await state.finish()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)