from sentence_transformers import SentenceTransformer
import numpy as np
from pymilvus import MilvusClient

# Setting up MilvusClient (serverless mode)
DATABASE_FILE = "milvus_demo.db"
COLLECTION_NAME = "journal_vectors"
VECTOR_DIMENSION = 384

# Load SentenceTransformer model
model = SentenceTransformer('all-MiniLM-L6-v2')

def setup():
    # Initialize the MilvusClient
    client = MilvusClient(DATABASE_FILE)

    # Check if the collection exists, drop it if needed
    if client.has_collection(collection_name=COLLECTION_NAME):
        client.drop_collection(collection_name=COLLECTION_NAME)
        print(f"Collection '{COLLECTION_NAME}' dropped.")

    # Create a new collection
    client.create_collection(
        collection_name=COLLECTION_NAME,
        dimension=VECTOR_DIMENSION,
    )
    print(f"Collection '{COLLECTION_NAME}' created.")
    return client

# Function to store vectors in Milvus
def store_vectors(data,client):
    # vectors = [item['vector'] for item in data]
    ids = client.insert(
        collection_name=COLLECTION_NAME,
        data=data,
    )
    print(f"Inserted {len(ids)} vectors into '{COLLECTION_NAME}' with IDs: {ids}")
    return ids

# Create embeddings
def create_embeddings(titles):
    embeddings = model.encode(titles).tolist()

    # Prepare data in the required format
    data = [
        {"id": i, "vector": embeddings[i], "text": titles[i], "subject": "oncology"}
        for i in range(len(titles))
    ]
    return data

# Querying Milvus
# Function to query the collection with a free-text query
def query_milvus(query_text, client, top_k=5):
    # Generate embedding for the query text
    query_embedding = model.encode([query_text]).tolist()[0]

    # Perform search in the collection
    search_results = client.search(
        collection_name=COLLECTION_NAME,
        data=[query_embedding],
        limit=top_k,
    )

    # Parse and display results
    # print(f"Query: {query_text}")
    return search_results
    # for i, result in enumerate(search_results[0]):
        # print(f"Rank {i+1}: ID = {result.id}, Distance = {result.distance}")
