from scraper import fetch_oncology_articles
from database1 import create_database, create_table, save_to_database
from milvus_db3 import setup, store_vectors, create_embeddings, query_milvus

def main(query):
    # Fetch articles
    titles, authors, date, abstracts = fetch_oncology_articles()

    # Create database and table
    create_database()
    create_table()

    # Save articles to database
    save_to_database(titles, authors, date, abstracts)

    # Setup Milvus
    client = setup()

    # Create embeddings
    data = create_embeddings(titles)

    # Store vectors in Milvus
    store_vectors(data, client)

    # Search articles
    result = query_milvus(query, client)
    print(result)
    return result

if __name__ == "__main__":
    query = "Give me the journals published last week"
    main(query)