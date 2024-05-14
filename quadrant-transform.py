import pandas as pd
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from sentence_transformers import SentenceTransformer

# Read the CSV file
df = pd.read_csv('filtered_formatted_ctf_writeups.csv')

# Initialize the Qdrant client
client = QdrantClient(host='localhost', port=6333)

# Create a new collection in Qdrant
collection_name = 'ctf_writeups'
vector_size = 384  # Adjust the vector size based on the chosen model
client.recreate_collection(
    collection_name=collection_name,
    vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE)
)

# Load the sentence transformer model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Function to generate embeddings for a given text
def generate_embedding(text):
    embedding = model.encode(text)
    return embedding.tolist()

# Iterate over each row in the DataFrame
for index, row in df.iterrows():
    title = row['title']
    url = row['url']
    tags = row['tags']
    description = row['description']
    
    # Generate embedding for the description
    embedding = generate_embedding(description)
    
    # Create a payload for the row
    payload = {
        'title': title,
        'url': url,
        'tags': tags,
        'description': description
    }
    
    # Insert the vector and payload into Qdrant
    client.upsert(
        collection_name=collection_name,
        points=[
            {
                'id': index,
                'vector': embedding,
                'payload': payload
            }
        ]
    )

print("Embeddings generated and inserted into Qdrant.")
