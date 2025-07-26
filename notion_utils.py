import os
from notion_client import Client
from datetime import datetime

print("in notion.utils -> \n")

# Хардкод временно (или возьми из env, если работает)
NOTION_TOKEN = "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"

# 💥 ВАЖНО: правильно инициализируй клиент
notion = Client(auth=NOTION_TOKEN)
print("TOKEN USED in notion_utils:", notion)

NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")




# Привязка Telegram ID к пользователю в Notion
NOTION_PEOPLE = {
    524373106: {"name": "Amir", "id": "some-notion-user-id"},       # Заполни, если нужно персонально
    501421236: {"name": "Temir"},
    5006534774: {"name": "Alemkhan"},
    897190202: {"name": "Damir"},
    385608549: {"name": "Bekzhan"},
    501352218: {"name": "Daniyal"},
    123456789: {"name": "Abdulla"},
}

def format_date():
    return datetime.now().strftime("%Y-%m-%d")

async def send_to_notion(user_id, data):
    developer_info = NOTION_PEOPLE.get(user_id, {"name": f"User {user_id}"})

    try:
        notion.pages.create(
            parent={"database_id": NOTION_DATABASE_ID},
            properties={
                "Date": {
                    "date": {"start": format_date()}
                },
                "Developer Name": {
                    "people": []  # Можно оставить пустым, если не хочешь ассайнить
                },
                "Day Summary": {
                    "rich_text": [{"text": {"content": data["q1"]}}]
                },
                "Difficulties": {
                    "rich_text": [{"text": {"content": data["q2"]}}]
                },
                "tomorrow_plan": {
                    "rich_text": [{"text": {"content": data["q3"]}}]
                },
                "Comments": {
                    "rich_text": [{"text": {"content": data["q4"]}}]
                }
            }
        )
        print(f"✅ Отчёт от {developer_info['name']} успешно отправлен в Notion.")
    except Exception as e:
        print(f"❌ Ошибка при отправке в Notion: {e}")
