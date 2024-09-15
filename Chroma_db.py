# chroma_setup.py
import chromadb
from sentence_transformers import SentenceTransformer

# Initialize ChromaDB client
client = chromadb.Client()

# Create a new collection in ChromaDB
collection = client.create_collection(
    name='documents',
    schema={
        'id': chromadb.TEXT(),
        'title': chromadb.TEXT(),
        'content': chromadb.TEXT(),
        'embedding': chromadb.VECTOR(dimension=768)  # Adjust based on your model
    }
)

# Load a pre-trained model for encoding documents
model = SentenceTransformer('distilbert-base-nli-stsb-mean-tokens')

# Example documents
documents = [
    {'id': '1', 'title': 'Document 1', 'content': 'This is the content of document 1.'},
    {'id': '2', 'title': 'Document 2', 'content': 'Content of the second document.'},
]

# Encode and insert documents into ChromaDB
for doc in documents:
    embedding = model.encode(doc['content']).tolist()
    collection.insert(
        {
            'id': doc['id'],
            'title': doc['title'],
            'content': doc['content'],
            'embedding': embedding
        }
    )

# Verify the insertions
all_docs = collection.find_all()
print(f"Total documents in collection: {len(all_docs)}")
