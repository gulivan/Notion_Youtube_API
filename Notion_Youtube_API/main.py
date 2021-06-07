import os
import json
import requests
from dotenv import load_dotenv
load_dotenv()
NOTION_ENDPOINT = "https://api.notion.com/v1/pages"
NOTION_SECRET = os.getenv("NOTION_SECRET")
TARGET_DB = os.getenv("TARGET_DB")


class NotionData:
    data = {"properties": {}}
    headers = {"Content-Type": "application/json", "Notion-Version": "2021-05-13"}

    def __init__(self, notion_secret: str, target_db: str):
        self.target_db = target_db
        self.notion_secret = notion_secret
        self.data["parent"] = {"database_id": target_db}
        self.headers["Authorization"] = f"Bearer {notion_secret}"

    def add_property(self, field_name: str, value: str, property_type: str = 'title'):
        if field_name in self.data["properties"]:
            raise ValueError(
                f"A property named {field_name} already exists in this new entry."
            )
        self.data["properties"][field_name] = {f"{property_type}": [{"text": {"content": f"{value}"}}]}

    def publish_row(self):
        r = requests.post(url=NOTION_ENDPOINT,
                          data=json.dumps(self.data),
                          headers=self.headers)
        if r.status_code != 200:
            raise ValueError(
                f"Error code: {r.json()['code']}. Message: {r.json()['message']}"
            )
        return True


notion = NotionData(notion_secret=NOTION_SECRET, target_db=TARGET_DB)
notion.add_property(field_name='Name', value='fsadfafds')
notion.publish_row()
