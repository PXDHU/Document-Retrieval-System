# app.py

from flask import Flask, request, jsonify
import chromadb
from sentence_transformers import SentenceTransformer

app = Flask(__name__)

# Initialize ChromaDB client and load model
client = chromadb.Client()
collection = client.get_collection(name='documents')
model = SentenceTransformer('distilbert-base-nli-stsb-mean-tokens')


def search_similar_documents(query, top_k=5):
    # Encode the query
    query_embedding = model.encode(query).tolist()

    # Perform similarity search
    results = collection.find_similar(
        'embedding', query_embedding, top_k=top_k
    )
    return results


@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "API is active"})


@app.route('/search', methods=['POST'])
def search():
    data = request.json
    text = data.get('text')
    top_k = data.get('top_k', 5)

    # Query ChromaDB for similar documents
    results = search_similar_documents(text, top_k)

    # Format results
    response = [{'title': r['title'], 'content': r['content']} for r in results]
    return jsonify(response)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
