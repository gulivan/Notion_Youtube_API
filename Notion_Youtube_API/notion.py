import json
from typing import Union, Dict, Optional, List, Any
import requests
NOTION_ENDPOINT_PAGES = "https://api.notion.com/v1/pages/"
NOTION_ENDPOINT_DATABASES = "https://api.notion.com/v1/databases/"
NOTION_VERSION = "2021-05-13"


class Notion:
    data = {"properties": {}}
    headers = {"Content-Type": "application/json",
               "Notion-Version": NOTION_VERSION}
    property_types = ["title", "rich_text", "number", "select", "multi_select", "date", "people", "file", "checkbox",
                      "url", "email", "phone_number", "formula", "relation", "rollup", "created_time", "created_by",
                      "last_edited_time", "last_edited_by"]

    def __init__(self, notion_secret: str, target_db: str):
        self.target_db = target_db
        self.notion_secret = notion_secret
        self.data["parent"] = {"database_id": target_db}
        self.headers["Authorization"] = f"Bearer {notion_secret}"

    def add_property(self,
                     field_name: str,
                     value: Union[str, Dict[str, str]],
                     link: Optional[str] = None,
                     property_type: str = 'title',
                     overwrite: bool = False):
        """
        Adds a new data property to the row
        :param str field_name: Field name in the table
        :param str value: Field value
        :param str link:
        :param str property_type: Field type.
        For more: https://developers.notion.com/reference/database#database-properties
        :param bool overwrite: If True - overwrites value with the same name
        """
        if field_name in self.data["properties"] and not overwrite:
            raise ValueError(
                f"A property named {field_name} already exists in this entry."
            )
        if property_type == 'text':
            property_type = 'rich_text'
        if link and property_type != 'rich_text':
            raise ValueError(
                f"Link type is compatible only with the \"rich_text\" property_type"
            )

        if property_type == 'title':
            self.data["properties"][field_name] = {property_type: [{"text": {"content": value}}]}
        elif property_type == 'url':
            self.data["properties"][field_name] = {property_type: value}
        elif property_type == 'rich_text':
            if link:
                self.data["properties"][field_name] = {property_type: [{"text": {"content": value,
                                                                                 "link": {"url": link}}}]}
            else:
                self.data["properties"][field_name] = {property_type: [{"text": {"content": value}}]}
        elif property_type in self.property_types:
            raise ValueError(
                f"The property_type {property_type} is not supported yet"
            )
        else:
            raise ValueError(
                f"Invalid property_type: {property_type}"
            )
        # there is no way to add custom "select" or "multi-select" tag
        # with current API V1 (confirmed by the Notion support service)
        # elif property_type == 'select':
        #     self.data["properties"][field_name] = {property_type: value}

    def publish_row(self,
                    print_curl: bool = False,
                    clean_data: bool = False):
        """
        Publish a row with an object data to database.
        :param print_curl: Prints CURL command for debug purposes
        :param clean_data: Resets data to the initial state
        """
        r = requests.post(url=NOTION_ENDPOINT_PAGES,
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
        if clean_data:
            self.data = {"properties": {}, "parent": {"database_id": self.target_db}}
        return True

    def get_database(self,
                     database_id: Optional[str] = None,
                     start_cursor: Optional[str] = None):
        def extract_values(results: List[Any]) -> List[List[str]]:
            data_accumulator = []
            for result in results:
                try:
                    playlist_url = result['properties']['Playlist']['rich_text'][0]['href']
                    video_url = result['properties']['Link']['url']
                except (KeyError, IndexError):
                    playlist_url = ''
                    video_url = ''
                data_accumulator.append([playlist_url, video_url])
            return data_accumulator

        if not database_id:
            database_id = self.target_db
        target_url = f"{NOTION_ENDPOINT_DATABASES}{database_id}/query"
        # data = {"start_cursor": )
        if start_cursor:
            data = {'start_cursor': start_cursor}
            r = requests.post(target_url,
                              headers=self.headers,
                              data=json.dumps(data))
        else:
            r = requests.post(target_url,
                              headers=self.headers)
        result_data = extract_values(r.json()['results'])
        if r.json().get('has_more'):
            start_cursor = r.json().get('next_cursor')
            result_data.extend(self.get_database(database_id, start_cursor=start_cursor))
        return result_data
