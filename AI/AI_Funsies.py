from AIQuery import get_relevant_document
from AIQuery import get_response
from Embeddings import get_embedding

string = "I am interested in theoretical computer science"
print(get_relevant_document(string))
