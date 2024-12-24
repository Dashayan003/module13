from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio


api = ''
bot = Bot(token=api)
dp = Dispatcher(bot, storage=MemoryStorage())


keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
button_calculate = KeyboardButton(text="Рассчитать")
button_info = KeyboardButton(text="Информация")
keyboard.add(button_calculate, button_info)


inline_keyboard = InlineKeyboardMarkup()
inline_button_calories = InlineKeyboardButton(
    text="Рассчитать норму калорий", callback_data="calories"
)
inline_button_formulas = InlineKeyboardButton(
    text="Формулы расчёта", callback_data="formulas"
)
inline_keyboard.add(inline_button_calories, inline_button_formulas)


@dp.message_handler(commands=['start'])
async def start_message(message):
    await message.answer(
        "Привет! Я бот, помогающий твоему здоровью. Выберите действие:",
        reply_markup=keyboard
    )


class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()


@dp.message_handler(text=['Рассчитать'])
async def main_menu(message):
    await message.answer(
        "Выберите опцию:",
        reply_markup=inline_keyboard
    )


@dp.callback_query_handler(text="formulas")
async def get_formulas(call):
    formula = ("Формула Миффлина-Сан Жеора:\n"
               "Мужчины: 10 × вес (кг) + 6.25 × рост (см) − 5 × возраст (лет) + 5\n"
               "Женщины: 10 × вес (кг) + 6.25 × рост (см) − 5 × возраст (лет) − 161")
    await call.message.answer(formula)
    await call.answer()


@dp.callback_query_handler(text=['calories'])
async def set_age(call):
    await call.message.answer("Введите свой возраст:")
    await UserState.age.set()
    await call.answer()


@dp.message_handler(state=UserState.age)
async def set_growth(message, state):
    await state.update_data(age=message.text)
    await message.answer("Введите свой рост:")
    await UserState.growth.set()


@dp.message_handler(state=UserState.growth)
async def set_weight(message, state):
    await state.update_data(growth=message.text)
    await message.answer("Введите свой вес:")
    await UserState.weight.set()


@dp.message_handler(state=UserState.weight)
async def send_calories(message, state):
    await state.update_data(weight=message.text)
    data = await state.get_data()

    age = int(data['age'])
    growth = int(data['growth'])
    weight = int(data['weight'])

    calories = 10 * weight + 6.25 * growth - 5 * age - 161

    await message.answer(f"Ваша норма калорий: {calories} ккал.")

    await state.finish()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
