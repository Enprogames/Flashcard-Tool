import requests
import json
import os

# open api_conf.json to get the api key
with open("src/api_conf.json", "r") as f:
    api_conf_json = json.load(f)

API_KEY = api_conf_json['api_key']
headers = {"Authorization": API_KEY, "Notion-Version": "2021-05-13"}
page_id = ""
notion_page_response = requests.get(f"https://api.notion.com/v1/pages/{page_id}", headers=headers)
#notion_page_response.raise_for_status()
notion_page = notion_page_response.json()

print(notion_page)