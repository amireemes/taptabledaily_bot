import os
from notion_client import Client
from datetime import datetime

print("in notion.utils -> \n")

# ✅ Используй переменную окружения или хардкод (временно)
NOTION_TOKEN = "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"
notion = Client(auth=NOTION_TOKEN)
print("TOKEN USED in notion_utils:", notion)

# ✅ Укажи ID базы данных
NOTION_DATABASE_ID = "23cf33d443d98012af65f0b879d550e1"

# ✅ Сопоставление Telegram ID <-> Notion User
NOTION_PEOPLE = {
    524373106: {"name": "Amir Yergaliyev", "id": "77e429c5-71bb-4fb6-81c3-4c6ae041afe7"},
    501421236: {"name": "Temirlan Ismagulov", "id": "1faeb36b-21be-47f1-8720-199e1f4079e8"},
    5006534774: {"name": "Alemkhan Yergaliyev", "id": "376ad707-ec57-4bf3-9376-765ee237b4eb"},
    1224720716: {"name": "Damir Kushembayev", "id": "207d872b-594c-81c5-abe9-00024958601a"},
    897190202: {"name": "Bekzhan Aktoreev", "id": "ebbd2e0d-d368-46aa-b639-1b4bb7007425"},
    501352218: {"name": "Daniyal Serik", "id": "f3a889de-9993-4ec2-ace5-dbee0fcbaaac"},
    123456789: {"name": "Abdulla Jurayev", "id": "48e3c66b-f93b-4dbf-a1a9-30f9d348532f"},
}

def format_date():
    return datetime.now().strftime("%Y-%m-%d")

async def send_to_notion(user_id, data):
    developer_info = NOTION_PEOPLE.get(user_id, {"name": f"User {user_id}"})

    try:
        notion.pages.create(
            parent={"database_id": NOTION_DATABASE_ID},
            properties={
                "title": {
                    "title": [
                        {
                            "text": {
                                "content": f"Отчёт от {developer_info['name']} на {format_date()}"
                            }
                        }
                    ]
                },
                "Date": {
                    "date": {"start": format_date()}
                },
                "Developer Name": {
                    "people": [{"id": developer_info["id"]}] if developer_info.get("id") else []
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
