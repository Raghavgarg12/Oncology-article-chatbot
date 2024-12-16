import requests
from bs4 import BeautifulSoup
import re
titles_list=[]
authors_list=[]
date_list=[]
abstract_list=[]

def clean_author_text(author_text):
    # Remove unwanted characters
    author_text = re.sub(r'\s*ORCID:.*?\d{4}-\d{4}-\d{4}-\d{4}.*?(?=,|$)', '', author_text)
    author_text = re.sub(r'\s*\xa0', ' ', author_text)
    author_text = re.sub(r',\s*,', ',', author_text)  # Remove extra commas
    return author_text.strip(', ')

def fetch_oncology_articles():
    base_url = "https://www.nature.com"
    search_url = "https://www.nature.com/search?subject=oncology&article_type=protocols%2Cresearch%2Creviews&page=1"

    while search_url:
        response = requests.get(search_url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            articles = soup.find_all('li', {'class': 'app-article-list-row__item'})

            for article in articles:
                try:
                    # Extract title and article link
                    title_tag = article.find('a', {'data-track-action': 'view article'})
                    title = title_tag.text.strip() if title_tag else 'N/A'
                    titles_list.append(title)
                    article_url = base_url + title_tag['href'] if title_tag else None

                    if article_url:
                        # Fetch article details
                        article_response = requests.get(article_url)
                        if article_response.status_code == 200:
                            article_soup = BeautifulSoup(article_response.text, 'html.parser')

                            # Extract author(s)
                            author_tag = article_soup.find('ul', {'class': 'c-article-author-list'})
                            if author_tag:
                              authors=""
                              for author in author_tag.find_all('li', {'class':"c-article-author-list__item"}):
                                  authors+=author.find('a').text+", "
                              authors_list.append(authors[:-2])
                            else:
                              authors_list.append("N/A")

                            # Extract publication date
                            date_tag = article_soup.find('time')
                            publication_date = date_tag['datetime'] if date_tag else 'N/A'
                            date_list.append(publication_date)

                            # Extract abstract
                            abstract_tag = article_soup.find('div', {'class': 'c-article-section__content'})
                            abstract = abstract_tag.text.strip() if abstract_tag else 'N/A'
                            abstract_list.append(abstract)
                
                except Exception as e:
                    print(f"Error processing an article: {e}")

            # Find next page
            next_page_tag = soup.find('a', {'class': 'c-pagination__link', 'data-track-action': 'next'})
            search_url = base_url + next_page_tag['href'] if next_page_tag else None

        else:
            print(f"Failed to fetch the webpage. Status code: {response.status_code}")
            break
        
    return titles_list,authors_list,date_list,abstract_list

if __name__ == "__main__":
    fetch_oncology_articles()
