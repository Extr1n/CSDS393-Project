from AI.AIQuery import get_relevant_document
from AI.AIQuery import get_response, get_major_requirements
from AI.Embeddings import get_embedding

string = "I am interested in theoretical computer science"
# print(get_relevant_document(string))

# print(get_response(string, ""))

print(get_major_requirements("Accounting, BS"))
