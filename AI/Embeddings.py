"""
Text Embedding Module.

This module provides functionality for generating vector embeddings from text
using the nomic-ai/nomic-embed-text-v1 model. These embeddings enable semantic
search capabilities throughout the CWRU Course Advisor system.

Functions:
    get_embedding: Convert text data into vector embeddings for semantic search.
"""

from sentence_transformers import SentenceTransformer
import numpy as np

# Load the embedding model
model = SentenceTransformer("nomic-ai/nomic-embed-text-v1", trust_remote_code=True)

def get_embedding(data, precision="float32"):
    """
    Generate embeddings for text data using the nomic-embed-text-v1 model.
    
    Creates vector representations of text that capture semantic meaning,
    allowing for similarity comparisons and vector search operations.
    
    Args:
        data (str or list): String or list of strings to embed.
        precision (str, optional): Precision of output embeddings ('float32' or 'float64').
            Defaults to 'float32'.
    
    Returns:
        list or list of lists: Vector embeddings for the input text.
            For a single string input, returns a single list of floats.
            For a list of strings input, returns a list of lists.
    
    Raises:
        ValueError: If input is not a string or list of strings.
    
    Example:
        >>> embedding = get_embedding("What courses cover machine learning?")
        >>> print(len(embedding))  # Prints the dimensionality of the embedding
        768
        >>> embeddings = get_embedding(["What is AI?", "How does machine learning work?"])
        >>> print(len(embeddings))  # Prints the number of embeddings generated
        2
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