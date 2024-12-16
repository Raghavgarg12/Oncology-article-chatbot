import mysql.connector
from mysql.connector import Error
import spacy
from spacy.lang.en.stop_words import STOP_WORDS
from collections import Counter
from string import punctuation
from heapq import nlargest
from scraper import fetch_oncology_articles
# Initialize SpaCy model
nlp = spacy.load("en_core_web_sm")

def create_database():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',  # Replace with your MySQL username
            password='raghav12'  # Replace with your MySQL password
        )

        if connection.is_connected():
            cursor = connection.cursor()
            cursor.execute("CREATE DATABASE IF NOT EXISTS OncologyArticles")
            print("Database created successfully")
    except Error as e:
        print(f"Error: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def create_table():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='OncologyArticles',
            user='root',
            password='raghav12'
        )

        if connection.is_connected():
            cursor = connection.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS articles (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    title VARCHAR(255),
                    author TEXT,
                    publication_date DATE,
                    abstract TEXT,
                    summary TEXT,
                    keywords TEXT
                )
            """
            )
            print("Table created successfully")
    except Error as e:
        print(f"Error: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def summarize_text(text):
    doc = nlp(text)
    word_frequencies = {}
    for word in doc:
        if word.text.lower() not in STOP_WORDS and word.text.lower() not in punctuation:
            if word.text.lower() not in word_frequencies:
                word_frequencies[word.text.lower()] = 1
            else:
                word_frequencies[word.text.lower()] += 1

    max_frequency = max(word_frequencies.values())
    for word in word_frequencies.keys():
        word_frequencies[word] = word_frequencies[word] / max_frequency

    sentence_tokens = [sent for sent in doc.sents]
    sentence_scores = {}
    for sent in sentence_tokens:
        for word in sent:
            if word.text.lower() in word_frequencies.keys():
                if sent not in sentence_scores.keys():
                    sentence_scores[sent] = word_frequencies[word.text.lower()]
                else:
                    sentence_scores[sent] += word_frequencies[word.text.lower()]

    select_length = int(len(sentence_tokens) * 0.3)
    summary = nlargest(select_length, sentence_scores, key=sentence_scores.get)
    final_summary = ' '.join([word.text for word in summary])
    return final_summary

def extract_keywords(text):
    doc = nlp(text)
    words = [token.text for token in doc if token.is_alpha and token.text.lower() not in STOP_WORDS]
    word_freq = Counter(words)
    keywords = [word for word, freq in word_freq.most_common(5)]
    return ', '.join(keywords)

def save_to_database(titles, authors, publication_dates, abstracts):
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='OncologyArticles',
            user='root',
            password='raghav12'
        )

        if connection.is_connected():
            cursor = connection.cursor()
            query = "INSERT INTO articles (title, author, publication_date, abstract, summary, keywords) VALUES (%s, %s, %s, %s, %s, %s)"

            for title, author, publication_date, abstract in zip(titles, authors, publication_dates, abstracts):
                summary = summarize_text(abstract)
                keywords = extract_keywords(abstract)
                cursor.execute(query, (title, author, publication_date, abstract, summary, keywords))

            connection.commit()
            print(f"{len(titles)} articles with summaries and keywords saved to database.")
    except Error as e:
        print(f"Error: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    # Example lists
    # titles = ["Title 1", "Title 2", "Title 3"]
    # authors = ["Author A", "Author B", "Author C"]
    # publication_dates = ["2024-01-01", "2024-02-01", "2024-03-01"]
    # abstracts = ["This is the first abstract. It contains important information about oncology.",
    #              "This is the second abstract. It provides insights into the latest research in oncology.",
    #              "This is the third abstract. It discusses advancements in oncology treatment methods."]

    titles, authors, publication_dates, abstracts = fetch_oncology_articles()
    create_database()
    create_table()
    save_to_database(titles, authors, publication_dates, abstracts)
