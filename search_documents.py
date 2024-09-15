from chromadb import Client
from sentence_transformers import SentenceTransformer
import chromadb.config as chroma_config

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

    return results


# Example usage
query = "Find documents related to this text"
search_results = search_documents(query)
for result in search_results:
    print(result['metadata']['text'])
