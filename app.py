from flask import Flask, request, jsonify
from chromadb import Client
from sentence_transformers import SentenceTransformer
import chromadb.config as chroma_config

app = Flask(__name__)

# Initialize ChromaDB and SentenceTransformer
chroma_client = Client(chroma_config.Settings(
    chroma_dir='chroma_db',
    persist_directory=True
))
collection = chroma_client.get_collection(name='documents')
model = SentenceTransformer('distilbert-base-nli-stsb-mean-tokens')


def search_documents(query_text, top_k=5):
    # Encode the query text
    query_embedding = model.encode(query_text).tolist()

    # Query ChromaDB for the most similar documents
    results = collection.query(embedding=query_embedding, top_k=top_k)

    # Extract relevant metadata from results
    extracted_results = [
        {"id": result['id'], "text": result['metadata']['text'], "score": result['score']}
        for result in results
    ]

    return extracted_results


@app.route('/search', methods=['POST'])
def search():
    data = request.json
    query_text = data.get('text')
    top_k = data.get('top_k', 5)

    if not query_text:
        return jsonify({"error": "Query text is required"}), 400

    # Perform the search
    search_results = search_documents(query_text, top_k=top_k)

    return jsonify(search_results)


@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "API is active"}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
