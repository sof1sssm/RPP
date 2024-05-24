import asyncio
import logging
import os
import datetime
import requests
import psycopg2
from aiogram import Dispatcher, Bot, Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, BotCommand, BotCommandScopeDefault

# Подключение к базе данных

conn = psycopg2.connect(dbname="rgz_rpp", user="sofia_andronovaa_knowlege_base",
                        password="123", host="127.0.0.1")
cursor = conn.cursor()

router = Router()

# Класс состояния для регистрации
class Registration(StatesGroup):
    waiting_for_login = State()

# Класс состояния для добавления операции
class AddOperation(StatesGroup):
    waiting_for_operation_type = State()
    waiting_for_amount = State()
    waiting_for_date = State()

# Команда /reg
@router.message(Command("reg"))
# Объявление функцийcmd_reg
async def cmd_reg(message: Message, state: FSMContext):
    # получаем идентификатор пользователя
    user_id = message.from_user.id
    # Проверяем, зарегистрирован ли пользователь
    cursor.execute("SELECT 1 FROM users WHERE user_id = %s", (user_id,))
    # Проверка результата выполнения запроса. cursor.fetchone используется для извлечения None
    if cursor.fetchone():
        await message.answer("Вы уже зарегистрированы!")
        return

    # Если не зарегистрирован, переводим в состояние ожидания логина
    await state.set_state(Registration.waiting_for_login)
    await message.answer("Введите ваш логин:")

# Обработчик состояния ожидания логина
@router.message(Registration.waiting_for_login)
async def process_login(message: Message, state: FSMContext):
    login = message.text
    user_id = message.from_user.id
    registration_date = datetime.datetime.now()

    # Сохраняем логин и дату регистрации в базу данных
    cursor.execute("INSERT INTO users (user_id, login, data) VALUES (%s, %s, %s)",
                   (user_id, login, registration_date))
    conn.commit()

    await state.clear()

    await message.answer(f"Вы успешно зарегистрированы с логином: {login}")

# Команда /lk
@router.message(Command("lk"))
async def cmd_lk(message: Message):
    user_id = message.from_user.id
    # Проверяем, зарегистрирован ли пользователь
    cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
    user_data = cursor.fetchone()

    if not user_data:
        await message.answer("Вы не зарегистрированы! Используйте команду /reg для регистрации.")
        return

    # Получаем количество операций
    cursor.execute("SELECT COUNT(*) FROM operations WHERE chat_id = %s", (user_id,))
    operation_count = cursor.fetchone()[0]

    # Выводим информацию пользователю
    await message.answer(f"""
Ваш профиль:
Логин: {user_data[1]}
Дата регистрации: {user_data[2].strftime('%Y-%m-%d %H:%M:%S')}
Количество операций: {operation_count}
""")

# Команда /add_operation
@router.message(Command("add_operation"))
async def cmd_add_operation(message: Message, state: FSMContext):
    user_id = message.from_user.id
    # Проверяем, зарегистрирован ли пользователь
    cursor.execute("SELECT 1 FROM users WHERE user_id = %s", (user_id,))
    if not cursor.fetchone():
        await message.answer("Вы не зарегистрированы! Используйте команду /reg для регистрации.")
        return

    # Предлагаем выбрать тип операции
    keyboard = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="РАСХОД"), KeyboardButton(text="ДОХОД")]
    ], resize_keyboard=True)
    await message.answer("Выберите тип операции:", reply_markup=keyboard)
    await state.set_state(AddOperation.waiting_for_operation_type)

# Обработчик выбора типа операции
@router.message(AddOperation.waiting_for_operation_type)
async def process_operation_type(message: Message, state: FSMContext):
    operation_type = message.text

    if operation_type not in ("РАСХОД", "ДОХОД"):
        await message.answer("Неверный тип операции. Выберите РАСХОД или ДОХОД.")
        return

    await state.update_data(operation_type=operation_type)

    if operation_type == "ДОХОД":
        # Добавить обработку ввода даты операции и сохранение в таблицу operations
        await message.answer("Введите дату операции (например, в формате ДД.ММ.ГГГГ):")
        await state.set_state(AddOperation.waiting_for_date)
    else:
        # Добавить вывод кнопок "НАЛИЧНЫЕ" и "КАРТА"
        keyboard = ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton(text="НАЛИЧНЫЕ"), KeyboardButton(text="КАРТА")]
        ], resize_keyboard=True)
        await message.answer("Выберите способ оплаты:", reply_markup=keyboard)
        await state.set_state(AddOperation.waiting_for_payment_method)


    # Сохраняем информацию в базе данных
    # Пример использования SQL-запроса для сохранения данных в таблицу operations
    cursor.execute("INSERT INTO operations (date, amount, user_id, operation_type, payment_method) VALUES (%s, %s, %s, %s, %s)",
                   (date, amount, user_id, operation_type, payment_method))
    connection.commit()

    # Сообщаем пользователю о том, что операция добавлена
    await message.answer("Операция успешно добавлена в базу данных.")

    # Сбрасываем состояние
    await state.finish()


# Обработчик ввода суммы операции
@router.message(AddOperation.waiting_for_amount)
async def process_amount(message: Message, state: FSMContext):
    try:
        amount = float(message.text)
    except ValueError:
        await message.answer("Неверный формат суммы. Введите число.")
        return

    await state.update_data(amount=amount)
    await message.answer("Укажите дату операции в формате YYYY-MM-DD:")
    await state.set_state(AddOperation.waiting_for_date)

# Обработчик ввода даты операции
@router.message(AddOperation.waiting_for_date)
async def process_date(message: Message, state: FSMContext):
    try:
        operation_date = datetime.datetime.strptime(message.text, "%Y-%m-%d").date()
    except ValueError:
        await message.answer("Неверный формат даты. Используйте YYYY-MM-DD.")
        return

    user_data = await state.get_data()
    operation_type = user_data['operation_type']
    amount = user_data['amount']
    user_id = message.from_user.id

    # Сохраняем операцию в базу данных
    cursor.execute("INSERT INTO operations (data, sum, chat_id, type_operation) VALUES (%s, %s, %s, %s)",
                   (operation_date, amount, user_id, operation_type))
    conn.commit()

    # Завершаем состояние добавления операции
    await state.clear()
    await message.answer("Операция успешно добавлена!")


async def main():
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    bot = Bot(token=bot_token)
    dp = Dispatcher()
    dp.include_router(router)

#    await bot.set_my_commands([
#        BotCommand(command='reg', description='Регистрация'),
#        BotCommand(command='lk', description='Личный кабинет'),
#        BotCommand(command='add_operation', description='Добавить операцию')
#    ], scope=BotCommandScopeDefault())

    await dp.start_polling(bot)

class ViewOperations(StatesGroup):
    waiting_for_currency = State()

@router.message(Command("operations"))
async def operations(message: Message, state: FSMContext):
    user_id = message.from_user.id

    # Check if the user is registered
    cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
    user = cursor.fetchone()

    if not user:
        await message.answer('Вы не зарегистрированы! Для регистрации используйте команду /reg')
        return

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="RUB"), KeyboardButton(text="EUR"), KeyboardButton(text="USD")],
        ],
        resize_keyboard=True
    )
    await message.answer("Выберите валюту:", reply_markup=keyboard)
    await state.set_state(ViewOperations.waiting_for_currency)

@router.message(ViewOperations.waiting_for_currency)
async def process_currency(message: Message, state: FSMContext):
    currency = message.text.upper()

    if currency not in ("RUB", "EUR", "USD"):
        await message.answer("Пожалуйста, выберите валюту, используя кнопки.")
        return

    user_id = message.from_user.id
    # Fetch operations from the database
    cursor.execute("SELECT * FROM operations WHERE chat_id = %s::varchar", (user_id,))
    operations = cursor.fetchall()

    if not operations:
        await message.answer("У вас пока нет операций.")
        return

    output = ""
    if currency == "RUB":
        for operation in operations:
            if operation[3] == "РАСХОД":
                # Add payment method to the output for EXPENSE operations
                output += f"Дата: {operation[0]}, Тип: {operation[3]}, Сумма: {operation[1]} RUB, Способ оплаты: {operation[4]}\n"
            else:
                output += f"Дата: {operation[0]}, Тип: {operation[3]}, Сумма: {operation[1]} RUB\n"
    else:
        try:
            response = requests.get(f"http://195.58.54.159:8000/rate?currency={currency}")
            response.raise_for_status()  # Check for HTTP errors

            rate = response.json()["rate"]
            for operation in operations:
                converted_amount = float(operation[1]) / rate
                if operation[3] == "РАСХОД":
                    output += f"Дата: {operation[0]}, Тип: {operation[3]}, Сумма: {converted_amount:.2f} {currency}, Способ оплаты: {operation[4]}\n"
                else:
                    output += f"Дата: {operation[0]}, Тип: {operation[3]}, Сумма: {converted_amount:.2f} {currency}\n"
        except requests.exceptions.RequestException as e:
            await message.answer(f"Ошибка при получении курса валют: {e}")
            await state.clear()
            return

    await message.answer(output)
    await state.clear()


async def main():
    bot_token = os.getenv('API-TOKEN')
    bot = Bot(token=bot_token)
    dp = Dispatcher()
    dp.include_router(router)

    await bot.set_my_commands([
        BotCommand(command='reg', description='Регистрация'),
        BotCommand(command='lk', description='Личный кабинет'),
        BotCommand(command='add_operation', description='Добавить операцию'),
        BotCommand(command='operations', description='Просмотреть операции')
    ], scope=BotCommandScopeDefault())

    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())

cursor.close()
conn.close()