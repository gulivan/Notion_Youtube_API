import os
import json
from typing import Union, Dict
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

    def add_property(self,
                     field_name: str,
                     value: Union[str, Dict[str, str]],
                     property_type: str = 'title',
                     overwrite: bool = False):
        """
        Adds a new data property to the row
        :param str field_name: Field name in the table
        :param str value: Field value
        :param str property_type: Field type.
        For more: https://developers.notion.com/reference/database#database-properties
        :param bool overwrite: If True - overwrites value with the same name
        """
        if field_name in self.data["properties"] and not overwrite:
            raise ValueError(
                f"A property named {field_name} already exists in this entry."
            )
        if property_type == 'title':
            self.data["properties"][field_name] = {property_type: [{"text": {"content": value}}]}
        elif property_type == 'url':
            self.data["properties"][field_name] = {property_type: value}
        elif property_type == 'select':
            self.data["properties"][field_name] = {property_type: value}

    def publish_row(self, print_curl=False):
        r = requests.post(url=NOTION_ENDPOINT,
                          data=json.dumps(self.data),
                          headers=self.headers)
        if print_curl:
            req = r.request
            command = "curl -X {method} -H {headers} -d '{data}' '{uri}'"
            method = req.method
            uri = req.url
            data = req.body
            headers = ['"{0}: {1}"'.format(k, v) for k, v in req.headers.items()]
            headers = " -H ".join(headers)
            print(command.format(method=method, headers=headers, data=data, uri=uri))
        if r.status_code != 200:
            raise ValueError(
                f"Error code: {r.json()['code']}. Message: {r.json()['message']}"
            )
        return True


notion = NotionData(notion_secret=NOTION_SECRET,
                    target_db=TARGET_DB)
notion.add_property(field_name='Title',
                    property_type='title',
                    value='Video title')
notion.add_property(field_name='Link',
                    property_type='url',
                    value='https://ya.ru')
notion.add_property(field_name='Playlist',
                    property_type='select',
                    value={"name": "non existing select"})
notion.publish_row(print_curl=True)

print(42)
