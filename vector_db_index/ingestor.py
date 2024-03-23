import os
import requests
import json
import time

from tqdm import tqdm

import together
import pymongo
# from newsapi import NewsApiClient

TOGETHER_API_KEY = os.environ['TOGETHER_API_KEY']
MONGODB_URI = os.environ['MONGODB_URI']
# NEWS_API_KEY = os.environ['NEWS_API_KEY']

EMBEDDING_MODEL = 'togethercomputer/m2-bert-80M-32k-retrieval'
EMBEDDING_FIELD = 'article_embedding'

together.api_key = TOGETHER_API_KEY
client = pymongo.MongoClient(MONGODB_URI)
# newsapi = NewsApiClient(api_key=NEWS_API_KEY)

def generate_embedding_together(text):
  url = "https://api.together.xyz/api/v1/embeddings"
  headers = {
	"accept": "application/json",
	"content-type": "application/json",
	"Authorization": f"Bearer {TOGETHER_API_KEY}"
  }
  session = requests.Session()
  response = session.post(
	  url,
	  headers=headers,
	  json={"input": text,
			"model": EMBEDDING_MODEL
	  }
  )
  if response.status_code != 200:
  	raise ValueError(f"Request failed with status code {response.status_code}: {response.text}")
  return response.json()['data'][0]['embedding']


def construct_mongo_document(article):
	constructed_content = article["title"] + " " + article["description"] + " " + article["content"]
	doc = {
		"title": article["title"],
		"url": article["url"],
		"content": constructed_content,
		"source": article["source"]["name"],
		"date": article["publishedAt"],
		EMBEDDING_FIELD: generate_embedding_together(constructed_content)
	}
	return doc

def read_and_ingest_sentences(collection):
    

def fetch_and_ingest_news(collection, topic):
	print(f'Fetch and Ingesting News...')
	all_articles = newsapi.get_everything(q=topic,
										  from_param='2023-10-04',
										  language='en',
										  sort_by='relevancy',
										  page=2)
	for article in all_articles["articles"]:
		time.sleep(2)
		doc = construct_mongo_document(article)
		print(f'Inserting Docs Into Mongo...')
		collection.update_one({"url": doc["url"]}, {"$set": doc}, upsert= True)

if __name__ == "__main__":
	db = client.get_database('politics')
	collection = db["Sentences"]

	read_and_ingest_sentences(collection)
 