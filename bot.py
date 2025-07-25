from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio
import logging
import os

API_TOKEN = os.getenv("API_TOKEN")
USER_IDS = list(map(int, os.getenv("USER_IDS").split(',')))

# API_TOKEN = '7832088261:AAGzemM68XHFX9KumNpehCoTYfuy_uUiy1g'  # Заменить на свой токен
# USER_IDS = [524373106, 897190202, 501421236, 897190202, 385608549, 5006534774, 501352218]        # Сюда Telegram user ID разработчиков Amir, Damir, Temir, Bekzhan, ALem, Abdulla,

# FSM Состояния
class ReportStates(StatesGroup):
    question1 = State()
    question2 = State()
    question3 = State()
    question4 = State()

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
scheduler = AsyncIOScheduler()

incomplete_users = set()

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

async def send_daily_reports():
    for user_id in USER_IDS:
        incomplete_users.add(user_id)
        await bot.send_message(user_id, "1️⃣ Над какой задачей ты работал сегодня?")
        state = dp.current_state(user=user_id)
        await state.set_state(ReportStates.question1.state)

async def send_reminders():
    for user_id in list(incomplete_users):
        await bot.send_message(user_id, "⏰ Напоминание: пожалуйста, заполни ежедневный отчёт 🙌")

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    scheduler.add_job(send_daily_reports, 'cron', hour=17, minute=20)
    scheduler.add_job(send_reminders, 'cron', hour=17, minute=30)
    scheduler.start()
    executor.start_polling(dp, skip_updates=True)
