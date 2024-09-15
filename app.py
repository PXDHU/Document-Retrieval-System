import logging
import threading
import time
import requests
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify
import chromadb
from sentence_transformers import SentenceTransformer

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Initialize the Sentence Transformer model
model = SentenceTransformer('all-MiniLM-L6-v2')  # Replace with the model you are using

# Initialize the ChromaDB client
client = chromadb.Client()


# Function to encode text
def embed_text(text):
    return model.encode(text).tolist()


# Store document in ChromaDB
def store_document(title, link, embedding):
    # Assuming you have a collection set up in ChromaDB
    collection = client.get_or_create_collection('news_articles')
    collection.insert({
        'title': title,
        'link': link,
        'embedding': embedding
    })


# Function to scrape articles
def scrape_articles():
    url = 'https://example.com/rss'  # Replace with an actual RSS feed or news site URL
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'xml')

    articles = []
    for item in soup.find_all('item'):
        title = item.title.text
        link = item.link.text
        description = item.description.text

        articles.append({
            'title': title,
            'link': link,
            'description': description
        })
    return articles


# Function to store articles in the database
def store_article(article):
    title = article['title']
    link = article['link']
    description = article['description']

    # Encode the description
    embedding = embed_text(description)

    # Store the article and its embedding in the database
    store_document(title, link, embedding)


# Background thread to scrape and store articles periodically
def scrape_and_store():
    while True:
        try:
            articles = scrape_articles()
            # Update the database with new articles
            for article in articles:
                store_article(article)
            logger.info(f"Scraped and stored {len(articles)} articles.")
        except Exception as e:
            logger.error(f"Error in scraping articles: {e}")

        # Wait for a specified interval before scraping again (e.g., 1 hour)
        time.sleep(3600)


# Start the background thread
scraper_thread = threading.Thread(target=scrape_and_store)
scraper_thread.daemon = True  # Allows the thread to exit when the main program exits
scraper_thread.start()


# /health endpoint
@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "API is active"}), 200


# In-memory cache for simplicity
cache = {}

# Increment API call count for rate limiting
user_requests = {}


def increment_user_requests(user_id):
    if user_id not in user_requests:
        user_requests[user_id] = 0
    user_requests[user_id] += 1

    if user_requests[user_id] > 5:
        return False
    return True


def get_cached_results(cache_key):
    return cache.get(cache_key)


def cache_search_results(cache_key, results):
    cache[cache_key] = results


# /search endpoint
@app.route('/search', methods=['POST'])
def search():
    start_time = time.time()  # Start time for performance monitoring

    data = request.json
    query_text = data.get('text')
    top_k = data.get('top_k', 5)
    user_id = data.get('user_id')

    if not query_text or not user_id:
        logger.warning(f"Invalid request from user_id: {user_id}")
        return jsonify({"error": "Query text and user_id are required"}), 400

    # Rate limiting
    if not increment_user_requests(user_id):
        logger.warning(f"Rate limit exceeded for user_id: {user_id}")
        return jsonify({"error": "Rate limit exceeded"}), 429

    # Generate a unique cache key for the query
    cache_key = f"search:{query_text}:{top_k}"
    cached_results = get_cached_results(cache_key)

    if cached_results:
        logger.info(f"Cache hit for query: {query_text} by user_id: {user_id}")
        end_time = time.time()
        logger.info(f"Request processed in {end_time - start_time:.4f} seconds")
        return jsonify({"cached": True, "results": cached_results})

    # Perform the search
    logger.info(f"Cache miss for query: {query_text} by user_id: {user_id}")
    search_results = search_documents(query_text, top_k=top_k)

    # Cache the search results
    cache_search_results(cache_key, search_results)

    end_time = time.time()  # End time for performance monitoring
    logger.info(f"Request processed in {end_time - start_time:.4f} seconds")

    return jsonify({"cached": False, "results": search_results})


# Placeholder function for searching documents in the database
def search_documents(query_text, top_k=5):
    # Encode the query text
    query_embedding = embed_text(query_text)

    # Placeholder: retrieve documents based on the query_embedding
    # This is where you'd implement the logic to search in the ChromaDB database
    # and return the top_k documents most similar to the query_embedding
    # For now, let's return dummy data
    results = [
        {"title": "Dummy Article 1", "link": "http://example.com/1", "score": 0.9},
        {"title": "Dummy Article 2", "link": "http://example.com/2", "score": 0.85},
    ]

    return results[:top_k]


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
