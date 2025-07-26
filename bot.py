import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.utils.executor import start_polling
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
import locale
from notion_utils import send_to_notion
from notion_client import Client


# Переменные окружения
API_TOKEN = os.getenv("API_TOKEN")
USER_IDS = list(map(int, os.getenv("USER_IDS", "").split(','))) or [
    524373106, 1224720716, 501421236, 897190202, 385608549, 501352218, 5006534774] 
ADMINS = [524373106, 501421236, 5006534774]  # Amir, Temir, Alemkhan
DEVELOPERS = {
    524373106: "Amir Yergaliyev",
    1224720716: "Damir Kushumbayev",
    501421236: "Temirlan Ismagulov",
    897190202: "Bekzhan Aktoreev",
    385608549: "Alemkhan Yergaliyev",
    5006534774: "Abdulla Jurayev", 
    501352218: "Daniyal Serik"
}
GROUP_CHAT_ID = -1002827950178



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
scheduler = AsyncIOScheduler(event_loop=asyncio.get_event_loop())
incomplete_users = set()


# Обработчики команд и состояний
@dp.message_handler(commands=['report'])
async def start_report(message: types.Message):
    user_id = message.chat.id
    incomplete_users.add(user_id)
    await message.answer(
        "Привет! Хочу, чтобы ты рассказал мне о сегодняшнем дне 😎\n\n"
        "1. Над какой задачей ты работал сегодня? 🔪\n\n"
        "(Отпиши детально по нумерации задачи → Задача FXX: сделано это, это.\n"
        "Задача BKK: сделано это, это)"
    )
    await ReportStates.question1.set()

@dp.message_handler(state=ReportStates.question1)
async def q1(message: types.Message, state: FSMContext):
    await state.update_data(q1=message.text)
    await message.answer(
        "2. Какие были сложности? 👊\n\n"
        "(Может не хватало данных, были доработки на frontend/backend, баги и т.д.)"
    )
    await ReportStates.question2.set()

@dp.message_handler(state=ReportStates.question2)
async def q2(message: types.Message, state: FSMContext):
    await state.update_data(q2=message.text)
    await message.answer(
        "3. Что планируешь завтра? 📆\n\n"
        "(Опиши задачи, code review и т.п.)"
    )
    await ReportStates.question3.set()

@dp.message_handler(state=ReportStates.question3)
async def q3(message: types.Message, state: FSMContext):
    await state.update_data(q3=message.text)
    await message.answer(
        "4. Есть ли какие-нибудь комментарии? 📌\n\n"
        "(Любые важные замечания)"
    )
    await ReportStates.question4.set()


# Устанавливаем русскую локаль для форматирования дат (если поддерживается)
try:
    locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')
except locale.Error:
    # fallback: можно захардкодить месяц вручную или использовать другой подход
    MONTHS = {
        1: "января", 2: "февраля", 3: "марта", 4: "апреля",
        5: "мая", 6: "июня", 7: "июля", 8: "августа",
        9: "сентября", 10: "октября", 11: "ноября", 12: "декабря"
    }

# Месяцы на русском
MONTHS_RU = {
    1: "января", 2: "февраля", 3: "марта", 4: "апреля",
    5: "мая", 6: "июня", 7: "июля", 8: "августа",
    9: "сентября", 10: "октября", 11: "ноября", 12: "декабря"
}


@dp.message_handler(state=ReportStates.question4)
async def q4(message: types.Message, state: FSMContext):
    await state.update_data(q4=message.text)
    data = await state.get_data()

    today = datetime.now()
    formatted_date = f"{today.day} {MONTHS_RU[today.month]}"

    await message.answer("Спасибо, что нашёл время поделиться!\nТвой вклад ценен, ты крутой 😎")

    report_text = (
        f"📋 Твой отчёт на {formatted_date}:\n\n"
        f"1️⃣ Над чем работал:\n{data['q1']}\n\n"
        f"2️⃣ Сложности:\n{data['q2']}\n\n"
        f"3️⃣ План на завтра:\n{data['q3']}\n\n"
        f"4️⃣ Комментарии:\n{data['q4']}"
    )

    await message.answer(report_text)

    # Определяем имя разработчика
    developer_name = DEVELOPERS.get(message.chat.id, f"User {message.chat.id}")

    report_core = (
        f"1️⃣ Над чем работал:\n{data['q1']}\n\n"
        f"2️⃣ Сложности:\n{data['q2']}\n\n"
        f"3️⃣ План на завтра:\n{data['q3']}\n\n"
        f"4️⃣ Комментарии:\n{data['q4']}"
    )

    # # Отправляем отчёт администраторам
    # for admin_id in ADMINS:
    #     # if admin_id != message.chat.id:  # Чтобы не отправлять самому разработчику
    #         try:
    #             await bot.send_message(
    #                 admin_id,
    #                 f"🧑‍💻 Отчёт от {developer_name}:\n\n{report_core}"
    #             )
    #         except Exception as e:
    #             logging.warning(f"Не удалось отправить отчёт админу {admin_id}: {e}")
    
    # Отправка в группу
    try:
        await bot.send_message(
            GROUP_CHAT_ID,
            f"🧑‍💻 Отчёт от {developer_name} за {formatted_date}:\n\n{report_core}"
        )
        print("📤 Отправка в Notion:")
        print("ID:", message.chat.id)
        print("DATA:", data)
        print(f"TOKEN USED: {os.getenv('NOTION_TOKEN')}")


        await send_to_notion(message.chat.id, data)  

    except Exception as e:
        logging.warning(f"Не удалось отправить отчёт в группу: {e}")

# @dp.message_handler()
# async def catch_chat_id(message: types.Message):
#     print(f"Chat ID: {message.chat.id}")




# Задачи по расписанию
async def scheduled_send_daily_reports():
    for user_id in USER_IDS:
        incomplete_users.add(user_id)
        try:
            await bot.send_message(
    user_id,
    "Привет! Хочу, чтобы ты рассказал мне о сегодняшнем дне 😎\n\n"
    "1. Над какой задачей ты работал сегодня? 🔪\n\n"
    "(Отпиши детально по нумерации задачи → Задача FXX: сделано это, это.\n"
    "Задача BKK: сделано это, это)"
)
            state = dp.current_state(user=user_id)
            await state.set_state(ReportStates.question1.state)
        except Exception as e:
            logging.error(f"❌ Не удалось отправить сообщение пользователю {user_id}: {e}")

async def scheduled_send_reminders():
    for user_id in list(incomplete_users):
        try:
            await bot.send_message(user_id, "⏰ Напоминание: пожалуйста, заполни ежедневный отчёт 🙌")
        except Exception as e:
            logging.error(f"❌ Не удалось отправить напоминание пользователю {user_id}: {e}")


# Главная функция
async def main():
    logging.basicConfig(level=logging.INFO)

    # Запуск диспетчера и планировщика
    scheduler = AsyncIOScheduler(event_loop=asyncio.get_event_loop())  # привязка loop

    # Добавление асинхронных задач корректно
    # Алматы 19:25 → UTC 13:25

    scheduler.add_job(scheduled_send_daily_reports, trigger='cron', hour=18, minute=15, timezone='Asia/Almaty')
    scheduler.add_job(scheduled_send_reminders, trigger='cron', hour=19, minute=55, timezone='Asia/Almaty')

    scheduler.start()

    # Можно временно протестировать вручную:
    # await scheduled_send_daily_reports()
    # await scheduled_send_reminders()

    
    await dp.start_polling()

# Точка входа
if __name__ == '__main__':
    asyncio.run(main())
