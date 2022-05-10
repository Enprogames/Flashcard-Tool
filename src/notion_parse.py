#!/usr/bin/env python

import traceback
from typing import Dict, List, Tuple
import requests
import json
import os
import asyncio
import aiohttp

import numpy as np
import pandas as pd

api_dir = ""  # directory for the file to get the API key from

if os.path.exists("src/api_conf.json"):
    api_dir = "src/api_conf.json"
elif os.path.exists("api_conf.json"):
    api_dir = "api_conf.json"
elif os.path.exists("../api_conf.json"):
    api_dir = "../api_conf.json"
else:
    raise os.path.FileNotFoundError("The API key file was not found")

# open api_conf.json to get the api key
with open(api_dir, "r") as f:
    api_conf_json = json.load(f)

API_KEY = api_conf_json['api_key']
API_VERSION = '2022-02-22'

DEFAULT_HEADERS = {
    "Authorization": f"Bearer {API_KEY}", "Notion-Version": "2022-02-22", "Content-Type": "application/json"
}


class NotionDataFrame(pd.DataFrame):
    """_summary_A pandas dataframe which provides a quick and easy way to retrieve and use data from notion databases.
    Arguments for retrieval from notion must be provided either as instance variables or as arguments in
    the functions.

    Raises:
        AttributeError: If data hasn't been correctly passed before making http requests
    """

    # instance variables must be defined in this way for an extension of a pandas DataFrame
    _metadata = [
                 'api_key',
                 'db_id',
                 'api_version',
                 'db_json',
                 '_request_status',  # info about async data retrieval job: ['pending', 'success', 'error', 'cancelled']
                 '_load_status'  # info about asychronous initialization of data: ['pending', 'success', 'error', 'cancelled']
                ]

    @property
    def _constructor(self):
        return NotionDataFrame

    @property
    def request_status(self):
        if hasattr(self, '_request_status'):
            return self._request_status
        else:
            return None

    @property
    def load_status(self):
        if hasattr(self, '_load_status'):
            return self._load_status
        else:
            return None

    def parse_notion_datatype(self, data, datatype):
        """
        Possible datatypes: [text, number, select, multi_select, date, person, files & media, Checkbox, URL, Email, Phone, Formula]
        and all other ones are unsupported.
        """
        # from https://stackoverflow.com/a/11479840/6946463 
        options = {
            'title': self.parse_notion_title,
            'number': self.parse_notion_number,
            'rich_text': self.parse_notion_rich_text,
            'checkbox': self.parse_notion_checkbox
        }
        if datatype in options:
            return options[datatype](data)
        return None

    def parse_notion_title(self, data):
        if len(data) > 0:
            return data[0]['plain_text']
        else:
            return ""

    def parse_notion_number(self, data):
        if data:
            return float(data)
        return float(np.NaN)

    def parse_notion_rich_text(self, data):
        if data:
            return data[0]['text']['content']
        return ""

    def parse_notion_checkbox(self, data):
        if data:
            return bool(data)
        return False

    # def parse_notion_

    def parse_notion_database(self, db_json: Dict) -> Dict:
        """Notion databases return unruly json data which is formatted with each cell containing
        a json object for the given datatype

        Args:
            db_json (Dict): Notion database json. This can be requested using self.request_new()
        Returns:
            Dict: A dictionary of columns, ready to be inserted into a dataframe.
        """
        data_columns = {}
        for item in reversed(db_json):
            for column_label, column_data in reversed(item['properties'].items()):
                notion_type = column_data['type']
                data_object = column_data[notion_type]
                data_columns.setdefault(column_label, []).append(self.parse_notion_datatype(data_object, notion_type))

        return data_columns

    async def _request_new_data_job(self, db_id="", api_key="", api_version='2022-02-22'):
        """Send a request to notion to update the raw json data stored for that database
        This doesn't update the dataframe itself. It only updates the raw data stored for the database
        so that it can be parsed.

        Args:
            db_id (str, optional): _description_. Defaults to "".
            api_key (str, optional): _description_. Defaults to "".
            api_version (str, optional): _description_. Defaults to '2022-02-22'.
        """
        self._request_status = 'pending'

        db_url = f"https://api.notion.com/v1/databases/{self.db_id}/query"
        headers = {"Authorization": self.api_key, "Notion-Version": self.api_version, "Content-Type": "application/json"}
        # update the current json data for the database from notion
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.post(db_url) as response:
                resp_json = await response.json()
                try:
                    self.db_json = resp_json['results']
                    self._request_status = 'success'
                except KeyError:
                    message = "Some provided data, such as possibly the api key, was rejected by the notion server."
                    print(f"{message} Request URL: {db_url}. Request header: {headers}. Response: {resp_json}. Exception: {traceback.print_exc()}")
                    self._request_status = 'failed'

    def request_new(self, db_id="", api_key="", api_version="2022-02-22", asynchronous=False):

        self._request_status = 'pending'

        if db_id:
            self.db_id = db_id
        elif not hasattr(self, 'db_id'):
            raise AttributeError("db_id must be provided as instance variable or as a parameter")

        if api_key:
            self.api_key = api_key
        elif not hasattr(self, 'api_key'):
            raise AttributeError("api_key must be provided as an instance variable or as a parameter")

        if api_version:
            self.api_version = api_version
        elif not hasattr(self, 'api_version'):
            self.api_version = '2022-02-22'

        if asynchronous:
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

            # from https://stackoverflow.com/a/55409674/6946463
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:  # 'RuntimeError: There is no current event loop...'
                loop = None

            if loop and loop.is_running():
                print('Async event loop already running. Adding coroutine to the event loop.')
                tsk = loop.create_task(self._request_new_data_job(db_id=db_id, api_key=api_key, api_version=api_version))
                # ^-- https://docs.python.org/3/library/asyncio-task.html#task-object
                # Optionally, a callback function can be executed when the coroutine completes
                tsk.add_done_callback(
                    lambda t: print(f'Task done with result={t.result()}  << return val of main()'))
            else:
                print('Starting new event loop')
                asyncio.run(self._request_new_data_job(db_id=db_id, api_key=api_key, api_version=api_version))
            # asyncio.run(self._request_new_data_job(db_id=db_id, api_key=api_key, api_version=api_version))
        else:
            db_url = f"https://api.notion.com/v1/databases/{self.db_id}/query"
            headers = {"Authorization": self.api_key, "Notion-Version": self.api_version, "Content-Type": "application/json"}
            self.db_json = requests.post(db_url, headers=headers).json()['results']

        self._request_status = 'success'

    async def _load_data_job(self):
        self._load_status = 'pending'
        super().__init__(data=self.parse_notion_database(self.db_json))
        self._load_status = 'success'

    def load_data(self, asynchronous=False):
        """Load the current database json from self.db_json into the dataframe. This overwrites any previous data.
        """
        self._load_status = 'pending'
        if asynchronous:
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

            # from https://stackoverflow.com/a/55409674/6946463
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:  # 'RuntimeError: There is no current event loop...'
                loop = None

            if loop and loop.is_running():
                print('Async event loop already running. Adding coroutine to the event loop.')
                tsk = loop.create_task(self._load_data_job())
                # ^-- https://docs.python.org/3/library/asyncio-task.html#task-object
                # Optionally, a callback function can be executed when the coroutine completes
                tsk.add_done_callback(
                    lambda t: print(f'Task done with result={t.result()}  << return val of main()'))
            else:
                print('Starting new event loop')
                asyncio.run(self._load_data_job())
        else:
            super().__init__(data=self.parse_notion_database(self.db_json))
        self._load_status = 'success'

    async def _request_and_load_job(self, db_id="", api_key="", api_version='2022-02-22'):
        await self._request_new_data_job(db_id=db_id, api_key=api_key, api_version=api_version)
        await self._load_data_job()

    def request_and_load(self, db_id="", api_key="", api_version='2022-02-22', asynchronous=False):
        """
        """

        if db_id:
            self.db_id = db_id
        elif not hasattr(self, 'db_id'):
            raise AttributeError("db_id must be provided as instance variable or as parameter")

        if api_key:
            self.api_key = api_key
        elif not hasattr(self, 'api_key'):
            raise AttributeError("")

        if api_version:
            self.api_version = api_version
        elif not hasattr(self, 'api_version'):
            self.api_version = '2022-02-22'

        if asynchronous:
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
            asyncio.run(self._request_and_load_job(db_id=db_id, api_key=api_key, api_version=api_verison))
        else:
            # update self.db_json with new data from notion
            self.request_new(db_id=self.db_id, api_key=self.api_key, api_version=self.api_version, asychronous=False)
            # recreate the dataframe with the notion data
            self.load_data(asynchronous=False)


if __name__ == '__main__':
    import time

    notion_df = NotionDataFrame()
    print("initialized")
    notion_df.db_id = "a38d3a59-bdf8-4d7d-a341-79f431c8812e"
    notion_df.api_key = API_KEY
    notion_df.request_new(asynchronous=True)
    while notion_df.request_status == 'pending':
        print("still waiting...")
        time.sleep(0.5)  # wait half a second while still pending
    print(f"finished request with status: {notion_df.request_status}")
    if notion_df.request_status == 'success':
        notion_df.load_data(asynchronous=True)
        while notion_df.load_status == 'pending':
            print("still waiting...")
            time.sleep(0.5)
    # notion_db.request_and_load()
    print(notion_df.head(20))
    # notion_db.info()


def query_db(id):

    db_url = f"https://api.notion.com/v1/databases/{id}/query"

    response = requests.post(db_url, headers=DEFAULT_HEADERS)
    return response.json()


def search(query: str = "", api_key=API_KEY, api_version=API_VERSION):

    search_url = "https://api.notion.com/v1/search"

    DEFAULT_HEADERS = {
        "Authorization": f"Bearer {api_key}", "Notion-Version": api_version, "Content-Type": "application/json"
    }

    response = requests.post(search_url, headers=DEFAULT_HEADERS, json={"query": query})
    return response.json()


def list_dbs():

    search_url = "https://api.notion.com/v1/search"

    filter = {
        "value": "database"
    }

    filter = json.dumps({"filter": {"object": "database"}})
    response = requests.post(search_url, headers=DEFAULT_HEADERS, json={"filter": {"object": "database"}})
    return response.json()


def get_shared_dbs(api_key=API_KEY, api_version=API_VERSION):

    all_dbs = search(api_key=api_key, api_version=api_version)['results']

    db_names = {}

    for page in all_dbs:
        if 'title' in page:
            db_names[page['title'][0]['text']['content']] = page['id']

    return db_names


def get_flashcard_definition_dict(id) -> Dict[str, str]:
    """
    Return a dictionary in the format {term: definition} based on a given database
    """

    result: Dict[str, str] = {}

    content = query_db(id)['results']

    for item in content:
        data_row = item['properties']
        if 'Term' in data_row:
            if len(data_row['Term']['title']) > 0 and len(data_row['Definition']['rich_text']) > 0:
                if 'Exclude' in data_row:  # see if some cards are set to be excluded from the study sessions
                    if data_row['Exclude']['checkbox']:  # if the exclude checkbox is selected, continue without
                        continue
                term = data_row['Term']['title'][0]['text']['content']
                definition = data_row['Definition']['rich_text'][0]['text']['content']

                result[term] = definition

        else:
            print(f"error with row: {data_row}")

    return result


def get_flashcard_data_tuples(id) -> List[Tuple[str, str, bool]]:
    """
    Return a list of tuples of the form (term: str, definition: str, exclude: bool) based on a given notion database
    """

    result: List[Tuple[str, str, bool]] = []

    content = query_db(id)['results']

    for item in content:
        data_row = item['properties']

        if 'Term' in data_row and 'Definition' in data_row:
            if len(data_row['Term']['title']) > 0 and len(data_row['Definition']['rich_text']) > 0:
                term = data_row['Term']['title'][0]['text']['content']
                definition = data_row['Definition']['rich_text'][0]['text']['content']

                exclude = data_row['Exclude']['checkbox'] if 'Exclude' in data_row else False

                result.append((term, definition, exclude))

        elif 'Name' in data_row and 'Definition' in data_row:
            if len(data_row['Name']['title']) > 0 and len(data_row['Definition']['rich_text']) > 0:
                term = data_row['Name']['title'][0]['text']['content']
                definition = data_row['Definition']['rich_text'][0]['text']['content']

                exclude = data_row['Exclude']['checkbox'] if 'Exclude' in data_row else False

                result.append((term, definition, exclude))
        else:
            print(f"row incorrectly formatted: {data_row}")

    return result
