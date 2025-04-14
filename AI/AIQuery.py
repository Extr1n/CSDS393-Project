from dotenv import load_dotenv
from groq import Groq
from pymongo import MongoClient
import os
from AI.Embeddings import get_embedding

load_dotenv()

client = Groq()
mongo_client = MongoClient(os.getenv('DB_KEY'))
db = mongo_client.cluster0
courses_collection = db["Documents.Courses"]

chat_completion = client.chat.completions.create(
    #
    # Required parameters
    #
    messages=[
        # Set an optional system message. This sets the behavior of the
        # assistant and can be used to provide specific instructions for
        # how it should behave throughout the conversation.
        {
            "role": "system",
            "content": "You are an advisor for Case Western Reserve University."
        },
        # Set a user message for the assistant to respond to.
        {
            "role": "user",
            "content": "Hello!",
        }
    ],

    # The language model which will generate the completion.
    model="llama-3.3-70b-versatile",

    #
    # Optional parameters
    #

    # Controls randomness: lowering results in less random completions.
    # As the temperature approaches zero, the model will become deterministic
    # and repetitive.
    temperature=0.5,

    # The maximum number of tokens to generate. Requests can use up to
    # 32,768 tokens shared between prompt and completion.
    max_completion_tokens=1024,

    # Controls diversity via nucleus sampling: 0.5 means half of all
    # likelihood-weighted options are considered.
    top_p=1,

    # A stop sequence is a predefined or user-specified text string that
    # signals an AI to stop generating content, ensuring its responses
    # remain focused and concise. Examples include punctuation marks and
    # markers like "[end]".
    stop=None,

    # If set, partial message deltas will be sent.
    stream=False,
)

def get_response(prompt, document):
    load_dotenv()
    
    # Get relevant documents if none provided
    if not document:
        document = get_relevant_document(prompt)
    
    # Construct system prompt with retrieved document
    system_content = "You are an advisor for Case Western Reserve University and your response must include this information. Your goal is to help the user answer questions about courses and graduation requirements for their major. The user is only allowed to ask questions relating to CWRU's major requirements and/or courses.\n\n"
    
    if document:
        system_content += "Based on the available information, I can provide the following insights:\n\n" + document
    else:
        system_content += "I don't have specific information about that in my database. "
    
    system_content += "\n\nIf the user's question is not about CWRU's major requirements or courses, suggest they schedule a meeting with their 4-year advisor through MyJourney (https://journey.case.edu/s/)."
    
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt
            },
            {
                "role": "system",
                "content": system_content
            }
        ],
        model="llama-3.3-70b-versatile",
        temperature=0.5,
        max_completion_tokens=1024,
        top_p=1,
        stop=None,
        stream=False,
    )
    
    return chat_completion.choices[0].message.content

def get_relevant_document(prompt):
    """
    Creates an embedding for the user prompt and uses vector search to find relevant documents.
    Returns a formatted string containing the most relevant information from the database.
    """
    try:
        # Generate embedding for the user's prompt
        query_vector = get_embedding(prompt)
        
        # Perform vector search in MongoDB
        results = courses_collection.aggregate([
            {
                "$vectorSearch": {
                    "index": "vector_index",  # Your vector index name
                    "path": "description",    # Field containing embeddings
                    "queryVector": query_vector,
                    "numCandidates": 100,     # Number of candidate matches
                    "limit": 5                # Top results to return
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "code": 1,
                    "title": 1,
                    "description": 1,
                    "credits": 1,
                    "department": 1,
                    "score": {"$meta": "vectorSearchScore"}
                }
            }
        ])
        
        # Convert results to list
        results_list = list(results)
        
        # If no results found
        if not results_list:
            return "I couldn't find specific course information related to your question in the database."
        
        # Format the results into a readable document
        formatted_document = "Here are some relevant courses that might answer your question:\n\n"
        
        for course in results_list:
            formatted_document += f"Course: {course.get('code', 'N/A')} - {course.get('title', 'N/A')}\n"
            formatted_document += f"Credits: {course.get('credits', 'N/A')}\n"
            formatted_document += f"Department: {course.get('department', 'N/A')}\n"
            formatted_document += f"Description: {course.get('description', 'N/A')}\n\n"
        
        return formatted_document
        
    except Exception as e:
        print(f"Error in vector search: {str(e)}")
        return f"An error occurred while searching for relevant information: {str(e)}"