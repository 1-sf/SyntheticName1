from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

import os
import requests
import json
import time

import pymongo
from mistralai.client import MistralClient
from pymongo.server_api import ServerApi

MONGODB_URI = os.environ['MONGODB_URI']
mistral_client = MistralClient(api_key=os.environ['MISTRAL_API_KEY'])
client = pymongo.MongoClient(MONGODB_URI, server_api=ServerApi('1'))

EMBEDDING_FIELD = 'sentence_embedding'

def generate_embedding_mistral(sentence):
    embeddings_batch_response = mistral_client.embeddings(
        model="mistral-embed",
        input=[sentence],
    )
    return embeddings_batch_response.data[0].embedding

def retrieve_similar_sentences(db_collection, query, num_candidates=150, limit=10):
  query_emb = generate_embedding_mistral(query)

  results = db_collection.aggregate([
  {
    "$vectorSearch": {
      "index": "vector_index",
      "path": "sentence_embedding",
      "queryVector": query_emb,
      "numCandidates": 10,
      "limit": 10
    }
  }
])

  results = list(results)
  result_ids = list(map(lambda item: item['_id'], results))
  results = collection.find({"_id": {"$in": result_ids}}, {'sentence': 1})
  results = list(map(lambda item: item['sentence'], results))
  return results


if __name__ == "__main__":
  db = client.get_database('politics')
  collection = db["Sentences"]
  ## Example
  # retrieve_similar_sentences(collection, 'Lincoln ran for President in 1860 , sweeping the North in victory .')