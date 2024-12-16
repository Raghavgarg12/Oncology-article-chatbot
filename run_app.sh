#!/bin/bash

# Exit script on any error
set -e

echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Downloading SpaCy 'en_core_web_sm' model..."
python -m spacy download en_core_web_sm

# Prompt user for query input
echo "Enter the query to search in the vector database:"
read user_query

# Pass the query as an argument to app.py
echo "Running the application with the query: \"$user_query\""
python app.py "$user_query"
