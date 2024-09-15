from flask import Flask, request, jsonify
from search_documents import search_documents
import redis
import json
import logging
import time

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Initialize Redis client
redis_client = redis.Redis(host='localhost', port=6379, db=0)


def cache_search_results(key, data, expiration=300):
    # Cache the search results with a key and expiration time (in seconds)
    redis_client.setex(key, expiration, json.dumps(data))


def get_cached_results(key):
    # Get cached results if they exist
    cached_data = redis_client.get(key)
    if cached_data:
        return json.loads(cached_data)
    return None


def increment_user_requests(user_id, limit=5):
    # Track the number of requests a user makes
    key = f"user:{user_id}:requests"
    request_count = redis_client.get(key)

    if request_count:
        request_count = int(request_count)
        if request_count >= limit:
            return False
        redis_client.incr(key)
    else:
        # Set the initial request count and expiration time (e.g., 1 hour)
        redis_client.setex(key, 3600, 1)

    return True


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


@app.route('/health', methods=['GET'])
def health():
    # Simple endpoint to check if the API is running
    return jsonify({"status": "API is running"}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
