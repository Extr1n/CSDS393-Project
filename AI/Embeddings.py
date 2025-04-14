from sentence_transformers import SentenceTransformer
import numpy as np

# Load the embedding model
model = SentenceTransformer("nomic-ai/nomic-embed-text-v1", trust_remote_code=True)

def get_embedding(data, precision="float32"):
    """
    Generate embeddings for text data.
    
    Args:
        data: String or list of strings to embed
        precision: Precision of output embeddings ('float32' or 'float64')
    
    Returns:
        List or list of lists containing embeddings
    """
    try:
        # Handle both single strings and lists of strings
        if isinstance(data, str):
            embeddings = model.encode(data, precision=precision)
            return embeddings.tolist()
        elif isinstance(data, list):
            embeddings = model.encode(data, precision=precision)
            return [emb.tolist() for emb in embeddings]
        else:
            raise ValueError("Input must be a string or list of strings")
    except Exception as e:
        print(f"Error generating embeddings: {str(e)}")
        # Return a zero vector as fallback
        if isinstance(data, str):
            return [0.0] * 768  # Common embedding dimension
        else:
            return [[0.0] * 768 for _ in range(len(data))]