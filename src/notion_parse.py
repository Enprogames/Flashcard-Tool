import requests
import json
import os
from notion.client import NotionClient

# open api_conf.json to get the api key
with open("src/api_conf.json", "r") as f:
    api_conf_json = json.load(f)

API_KEY = api_conf_json['api_key']

client = NotionClient(token_v2=API_KEY)

page = client.get_block("https://www.notion.so/Charting-and-Technical-Analysis-89391759c30247ea8f09032107fd7946")

print(page.__dict__)
exit(0)

headers = {"Authorization": f"Bearer {API_KEY}", "Notion-Version": "2021-05-13", "Content-Type": "application/json"}
page_id = "89391759-c302-47ea-8f09-032107fd7946"

parameters = {"query": "Charting and Technical Analysis"}
notion_page_search = requests.get(f"https://api.notion.com/v1/search", headers=headers, params=parameters)
print(notion_page_search.json())

notion_page_response = requests.get(f"https://api.notion.com/v1/pages/{page_id}", headers=headers)
#notion_page_response.raise_for_status()
notion_page = notion_page_response.json()

print(notion_page)