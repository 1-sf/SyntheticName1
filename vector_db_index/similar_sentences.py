import sys
import os
from pymongo.server_api import ServerApi
from mistralai.client import MistralClient
import pymongo
from datasets import load_dataset
import pandas as pd
from dotenv import load_dotenv
import csv

# Load environment variables from the .env file
load_dotenv()

# from vector_db_index import rag

MONGODB_URI = os.environ['MONGODB_URI']
mistral_client = MistralClient(api_key=os.environ['MISTRAL_API_KEY'])
dataset = load_dataset("DFKI-SLT/cross_ner", "politics", split="test")

client = pymongo.MongoClient(MONGODB_URI, server_api=ServerApi('1'))


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
                "numCandidates": num_candidates,
                "limit": limit
            }
        }
    ])

    results = list(results)
    result_ids = list(map(lambda item: item['_id'], results))
    results = db_collection.find({"_id": {"$in": result_ids}}, {'sentence': 1})
    results = list(map(lambda item: item['sentence'], results))
    return results


def get_similar_sentences(collection, sentences, file_path):
    sentences_list = []
    print(len(sentences))
    i = 0
    try:
        for sentence in sentences:
            if i < 0:
                continue
            print('i=', i)
            similar_sentences = retrieve_similar_sentences(
                collection, sentence, num_candidates=6, limit=6)
            similar_sentences = list(
                filter(lambda s: s != sentence, similar_sentences))[:5]
            sentences_list.append([sentence] + similar_sentences)
            i += 1
    except:
        pass

    # Writing to CSV file
    with open(file_path, 'w', newline='') as csvfile:
        print('starting to write.................')
        csv_writer = csv.writer(csvfile)
        csv_writer.writerows(sentences_list)
        print('writing completed................')

def get_similar_sentences_french_kw(collection):
	df = pd.read_csv('data/scored/politics_tasklevel_french_kw.filt.csv')
	get_similar_sentences(
		collection, df['tokens'].to_list(), 'data/french_knn.csv')

def get_similar_sentences_dataset(collection):
	# File path to write the CSV file
	file_path = 'data/test_knn.csv'
	sentences = [" ".join(tokens) for tokens in dataset["tokens"]]
	get_similar_sentences(collection, sentences, file_path)


if __name__ == "__main__":
    db = client.get_database('politics')
    collection = db["Sentences"]
	# get_similar_sentences_dataset(collection)
    get_similar_sentences_french_kw(collection)
