from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

import os, sys
import requests
import json
import time

import together
import pymongo
from mistralai.client import MistralClient
from pymongo.server_api import ServerApi


MONGODB_URI = os.environ['MONGODB_URI']
mistral_client = MistralClient(api_key=os.environ['MISTRAL_API_KEY'])

EMBEDDING_FIELD = 'sentence_embedding'

client = pymongo.MongoClient(MONGODB_URI, server_api=ServerApi('1'))

def generate_batch_embeddings_mistral(sentences):
    embeddings_batch_response = mistral_client.embeddings(
        model="mistral-embed",
        input=sentences,
    )
    return [{'sentence': sentences[i], EMBEDDING_FIELD: embeddings_batch_response.data[i].embedding} for i in range(len(sentences))]

def read_and_ingest_sentences(collection):
    sentences = []
    with open("data/unlabeled/politics_tasklevel.txt", "r") as file:
        i = 0
        while True:
            line = file.readline()  # Read a single line
            if i < 0:
                i += 1
                continue
            if not line:  # Break out of the loop when the end of the file is reached
                break
            line = line.strip()
            sentences.append(line)
    batch_size = 100
    batches = [sentences[i:i+batch_size] for i in range(0, len(sentences), batch_size)]
    for batch in batches:
        embeddings_batch = generate_batch_embeddings_mistral(batch)
        collection.insert_many(embeddings_batch)

if __name__ == "__main__":
	db = client.get_database('politics')
	collection = db["Sentences"]

	read_and_ingest_sentences(collection)
 