"""
CWRU Course Advisor AI Package.

This package provides AI-powered tools for retrieving and providing information
about courses and graduation requirements at Case Western Reserve University.

Modules:
    AIQuery: Core module for generating AI responses about courses and requirements.
    Embeddings: Functionality for creating vector embeddings for semantic search.
    
Example usage:
    from AI.AIQuery import get_response
    
    response = get_response("What are the requirements for a Computer Science major?", 
                           user_major="Computer Science")
    print(response)
"""

from AI.AIQuery import get_response, get_major_requirements, get_relevant_document
from AI.Embeddings import get_embedding

__all__ = [
    'get_response',
    'get_major_requirements',
    'get_relevant_document',
    'get_embedding'
]