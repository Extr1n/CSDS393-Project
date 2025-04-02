from sentence_transformers import SentenceTransformer

# Load the embedding model
model = SentenceTransformer("nomic-ai/nomic-embed-text-v1", trust_remote_code=True)

# Define a function to generate embeddings
def get_embedding(data, precision="float32"):
   return model.encode(data, precision=precision).tolist()

