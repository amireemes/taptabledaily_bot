import os
from notion_client import Client
from datetime import datetime

print("in notion.utils -> \n")

# Хардкод временно (или возьми из env, если работает)
NOTION_TOKEN = "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"

# 💥 ВАЖНО: правильно инициализируй клиент
notion = Client(auth=NOTION_TOKEN)
print("TOKEN USED in notion_utils:", notion)

# NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")
NOTION_DATABASE_ID = "23cf33d443d98012af65f0b879d550e1"



# Привязка Telegram ID к пользователю в Notion
NOTION_PEOPLE = {
    524373106: {"name": "Amir Yergaliyev", "id": "77e429c5-71bb-4fb6-81c3-4c6ae041afe7"},
    501421236: {"name": "Temirlan Ismagulov", "id": "1faeb36b-21be-47f1-8720-199e1f4079e8"},
    385608549: {"name": "Alemkhan Yergaliyev", "id": "376ad707-ec57-4bf3-9376-765ee237b4eb"},
    1224720716: {"name": "Damir Kushembayev", "id": "207d872b-594c-81c5-abe9-00024958601a"},
    897190202: {"name": "Bekzhan Aktoreev", "id": "ebbd2e0d-d368-46aa-b639-1b4bb7007425"},
    501352218: {"name": "Daniyal Serik", "id": "f3a889de-9993-4ec2-ace5-dbee0fcbaaac"},
    5006534774: {"name": "Abdulla Jurayev", "id": "48e3c66b-f93b-4dbf-a1a9-30f9d348532f"}
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
