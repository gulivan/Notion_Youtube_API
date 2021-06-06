import os
import json
import requests

NOTION_ENDPOINT = "https://api.notion.com/v1/pages"
NOTION_SECRET = os.getenv('NOTION_SECRET')
TARGET_DB = os.getenv('TARGET_DB')

data = {
    "parent": { "database_id": f"{TARGET_DB}" },
    "properties": {
      "Name": {"title": [{"text": {"content": "sample text"}}]}
    }
}

class NotionData:
    body = {}
    headers = {"Content-Type": "application/json",
                "Notion-Version": "2021-05-13"}

    def __init__(self, notion_secret: str, target_db: str):
        self.target_db = target_db
        self.notion_secret = notion_secret
        self.body["parent"] = {"database_id": target_db}
        self.headers["Authorization"] = f"Bearer {notion_secret}"

notion = NotionData(notion_secret=NOTION_SECRET,
                    target_db=TARGET_DB)

r = requests.post(url=NOTION_ENDPOINT,
                  data=json.dumps(data),
                  headers=notion.headers)
print(r.json())
