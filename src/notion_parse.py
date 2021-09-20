#!/usr/bin/env python

from typing import Dict
import requests
import json
import os
from notion.client import NotionClient

# open api_conf.json to get the api key
with open("src/api_conf.json", "r") as f:
    api_conf_json = json.load(f)

API_KEY = api_conf_json['api_key']

#client = NotionClient(token_v2=f"{API_KEY}")
headers = {
        "Authorization": f"Bearer {API_KEY}", "Notion-Version": "2021-08-16", "Content-Type": "application/json"
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

def get_shared_dbs():

    all_dbs = search("")['results']

    db_names = {}

    for page in all_dbs:
        if 'title' in page:
            db_names[page['title'][0]['text']['content']] = page['id']

    return db_names

def get_flashcard_db_dict(id):

    content = query_db(id)['results']

    definitions = {}

    for item in content:
        data_row = item['properties']
        if len(data_row['Term']['title']) > 0 and len(data_row['Definition']['rich_text']) > 0:
            definitions[data_row['Term']['title'][0]['text']['content']] = data_row['Definition']['rich_text'][0]['text']['content']

    return definitions