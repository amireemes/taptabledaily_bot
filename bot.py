import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.utils.executor import start_polling
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from apscheduler.schedulers.asyncio import AsyncIOScheduler


from your_module import send_daily_reports, send_reminders  # замените на актуальный импорт

# Переменные окружения
API_TOKEN = os.getenv("API_TOKEN")
USER_IDS = list(map(int, os.getenv("USER_IDS", "").split(','))) or [
    524373106, 897190202, 501421236, 385608549, 5006534774, 501352218]

# FSM состояния
class ReportStates(StatesGroup):
    question1 = State()
    question2 = State()
    question3 = State()
    question4 = State()

# Инициализация
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
scheduler = AsyncIOScheduler()
incomplete_users = set()


# Обработчики команд и состояний
@dp.message_handler(commands=['report'])
async def start_report(message: types.Message):
    user_id = message.chat.id
    incomplete_users.add(user_id)
    await message.answer("1️⃣ Над какой задачей ты работал сегодня?")
    await ReportStates.question1.set()

@dp.message_handler(state=ReportStates.question1)
async def q1(message: types.Message, state: FSMContext):
    await state.update_data(q1=message.text)
    await message.answer("2️⃣ Какие были сложности?")
    await ReportStates.question2.set()

@dp.message_handler(state=ReportStates.question2)
async def q2(message: types.Message, state: FSMContext):
    await state.update_data(q2=message.text)
    await message.answer("3️⃣ Что планируешь завтра?")
    await ReportStates.question3.set()

@dp.message_handler(state=ReportStates.question3)
async def q3(message: types.Message, state: FSMContext):
    await state.update_data(q3=message.text)
    await message.answer("4️⃣ Есть ли какие-нибудь комментарии?")
    await ReportStates.question4.set()

@dp.message_handler(state=ReportStates.question4)
async def q4(message: types.Message, state: FSMContext):
    await state.update_data(q4=message.text)
    data = await state.get_data()
    await message.answer(
        f"📋 Твой отчёт:\n"
        f"1️⃣ Над чем работал: {data['q1']}\n"
        f"2️⃣ Сложности: {data['q2']}\n"
        f"3️⃣ План на завтра: {data['q3']}\n"
        f"4️⃣ Комментарии: {data['q4']}"
    )
    incomplete_users.discard(message.chat.id)
    await state.finish()


# Задачи по расписанию
async def scheduled_send_daily_reports():
    for user_id in USER_IDS:
        incomplete_users.add(user_id)
        await bot.send_message(user_id, "1️⃣ Над какой задачей ты работал сегодня?")
        state = dp.current_state(user=user_id)
        await state.set_state(ReportStates.question1.state)

async def scheduled_send_reminders():
    for user_id in list(incomplete_users):
        await bot.send_message(user_id, "⏰ Напоминание: пожалуйста, заполни ежедневный отчёт 🙌")


# Главная функция
async def main():
    logging.basicConfig(level=logging.INFO)

    scheduler.add_job(scheduled_send_daily_reports, 'cron', hour=18, minute=50)
    scheduler.add_job(scheduled_send_reminders, 'cron', hour=19, minute=30)
    scheduler.start()

    await dp.start_polling()


# Точка входа
if __name__ == '__main__':
    asyncio.run(main())
