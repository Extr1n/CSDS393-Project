"""
Example usage script for the CWRU Course Advisor AI.

This script demonstrates a simple example of using the AIQuery module
to retrieve course information based on a query about theoretical computer science.

Usage:
    Run this script directly to see a demo of the AI's response capabilities.
    python AI_Funsies.py
"""

from AIQuery import get_relevant_document
from AIQuery import get_response
from AI.Embeddings import get_embedding

def main():
    """
    Execute a sample query to demonstrate the functionality of the AI course advisor.
    
    Runs a query about theoretical computer science and prints the relevant
    course information retrieved from the database.
    
    Returns:
        None: Results are printed to standard output.
    """
    sample_query = "I am interested in theoretical computer science"
    print("Sample query:", sample_query)
    print("\nRetrieving relevant courses...\n")
    result = get_relevant_document(sample_query)
    print(result)

if __name__ == "__main__":
    main()