#!/usr/bin/env python

from typing import Dict, List, Tuple
import requests
import json
import os

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

headers = {
    "Authorization": f"Bearer {API_KEY}", "Notion-Version": "2022-02-22", "Content-Type": "application/json"
}


def get_db(id):
    """
    https://www.notion.so/2a59b9e1b3b9459eb5fdf64346408b38?v=de3c6ee6899a4173bee5ad1b4b4fbcaf
    """

    db_url = f"https://api.notion.com/v1/databases/{id}"

    response = requests.get(db_url, headers=headers)
    return response.json()


def query_db(id):

    db_url = f"https://api.notion.com/v1/databases/{id}/query"

    parameters = {"filter": {}}

    response = requests.post(db_url, headers=headers)
    return response.json()


def search(query: str = ""):

    search_url = f"https://api.notion.com/v1/search"

    response = requests.post(search_url, headers=headers, json={"query": query})
    return response.json()


def list_dbs():

    search_url = f"https://api.notion.com/v1/search"

    filter = {
        "value": "database"
    }

    filter = json.dumps({"filter": {"object": "database"}})
    response = requests.post(search_url, headers=headers, json={"filter": {"object": "database"}})
    return response.json()


def get_shared_dbs():

    all_dbs = search()['results']

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

        if 'Term' in data_row:
            if len(data_row['Term']['title']) > 0 and len(data_row['Definition']['rich_text']) > 0:
                term = data_row['Term']['title'][0]['text']['content']
                definition = data_row['Definition']['rich_text'][0]['text']['content']

                exclude = data_row['Exclude']['checkbox'] if 'Exclude' in data_row else False

                result.append((term, definition, exclude))

        elif 'Name' in data_row:
            if len(data_row['Name']['title']) > 0 and len(data_row['Definition']['rich_text']) > 0:
                term = data_row['Name']['title'][0]['text']['content']
                definition = data_row['Definition']['rich_text'][0]['text']['content']

                exclude = data_row['Exclude']['checkbox'] if 'Exclude' in data_row else False

                result.append((term, definition, exclude))
        else:
            print(f"row incorrectly formatted: {data_row}")

    return result
