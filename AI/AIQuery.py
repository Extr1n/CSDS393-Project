from dotenv import load_dotenv
from groq import Groq
from pymongo import MongoClient
import os
from Embeddings import get_embedding

load_dotenv()

client = Groq()

# Connect to MongoDB using your connection string.
# The database is "cluster0" with two separate collections for course metadata and embeddings,
# and one for requirements.
mongo_client = MongoClient(os.getenv('DB_KEY'))
db = mongo_client.cluster0

# Collections for course metadata and requirements (stored in Documents/courses and Documents/requirements)
courses_meta_collection = db["Documents.courses"]
requirements_collection = db["Documents.requirements"]

# Collection with course embeddings (vector index is built on this collection)
courses_embeddings_collection = db["cluster0.Documents.Courses"]

# An initial chat completion example (this sends a simple "Hello!" to the advisor model)
chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "system",
            "content": "You are an advisor for Case Western Reserve University."
        },
        {
            "role": "user",
            "content": "Hello!",
        }
    ],
    model="llama-3.3-70b-versatile",
    temperature=0.5,
    max_completion_tokens=1024,
    top_p=1,
    stop=None,
    stream=False,
)

def get_response(prompt, document, user_major=None):
    """
    Generate an AI response based on the user prompt and relevant documents.
    
    Args:
        prompt: The user's query.
        document: Relevant document information retrieved from the database.
        user_major: The user's major if available.
    
    Returns:
        AI-generated response text.
    """
    load_dotenv()
    
    # If no document was provided, retrieve relevant documents using vector search.
    if not document:
        document = get_relevant_document(prompt, user_major)
    
    # Build the system prompt with the retrieved information.
    system_content = (
        "You are an advisor for Case Western Reserve University. Your goal is to help the user answer questions "
        "about courses and graduation requirements for their major."
    )
    
    if user_major:
        system_content += f" The user's major is {user_major}."
    
    if document:
        system_content += "\n\nBased on the available information, here are the relevant details:\n\n" + document
    else:
        system_content += "\n\nI don't have specific information about that in my database."
    
    system_content += (
        "\n\nIf the user's question is not about CWRU's major requirements or courses, suggest they schedule a meeting with "
        "their 4-year advisor through MyJourney (https://journey.case.edu/s/)."
    )
    
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

def get_major_requirements(major):
    """
    Retrieve requirements for a specific major from the database.
    
    Args:
        major: The user's declared major.
    
    Returns:
        A formatted string containing major requirements.
    """
    try:
        # Perform a case-insensitive search for the major in the requirements collection.
        major_doc = requirements_collection.find_one(
            {"major": {"$regex": major, "$options": "i"}},
            {"_id": 0}
        )
        
        if not major_doc:
            return None
        
        formatted_requirements = f"Requirements for {major_doc.get('major', 'Unknown Major')}:\n\n"
        
        # Include core requirements if available.
        if 'core_requirements' in major_doc:
            formatted_requirements += "Core Requirements:\n"
            for course in major_doc['core_requirements']:
                formatted_requirements += f"- {course}\n"
            formatted_requirements += "\n"
        
        # Include elective requirements if available.
        if 'elective_requirements' in major_doc:
            formatted_requirements += "Elective Requirements:\n"
            formatted_requirements += f"{major_doc['elective_requirements']}\n\n"
        
        # Include additional requirements if available.
        if 'additional_requirements' in major_doc:
            formatted_requirements += "Additional Requirements:\n"
            formatted_requirements += f"{major_doc['additional_requirements']}\n\n"
        
        return formatted_requirements
    
    except Exception as e:
        print(f"Error retrieving major requirements: {str(e)}")
        return None

def get_relevant_document(prompt, user_major=None):
    """
    Create an embedding for the user prompt and use vector search on the courses embeddings collection.
    Also incorporates major requirements if available from the requirements collection.
    
    Args:
        prompt: The user's query.
        user_major: The user's declared major (optional).
    
    Returns:
        A string containing relevant document details.
    """
    try:
        final_document = ""
        
        if user_major:
            major_requirements = get_major_requirements(user_major)
            if major_requirements:
                final_document += major_requirements + "\n\n"
        
        # Generate the embedding vector for the prompt.
        query_vector = get_embedding(prompt)
        
        # Perform vector search in MongoDB
        pipeline = [
            {
                "$vectorSearch": {
                    "index": "vector_index",
                    "path": "embedding",    # Assuming the embedding field is called "embedding"
                    "queryVector": query_vector,
                    "numCandidates": 100,
                    "limit": 5,
                    "filter": {"department": user_major} if user_major else None 
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

        print(results)
        
        results = list(courses_collection.aggregate(pipeline))
        
        # If no results found
        if not results:
            if not final_document:
                return "I couldn't find specific information related to your question in the database."
            return final_document
        
        # Format the results into a readable document
        courses_info = "Here are some relevant courses that might answer your question:\n\n"
        
        for course in results:
            courses_info += f"Course: {course.get('code', 'N/A')} - {course.get('title', 'N/A')}\n"
            courses_info += f"Credits: {course.get('credits', 'N/A')}\n"
            courses_info += f"Department: {course.get('department', 'N/A')}\n"
            courses_info += f"Description: {course.get('description', 'N/A')}\n\n"
        
        final_document += courses_info
        return final_document
        
    except Exception as e:
        print(f"Error in vector search: {str(e)}")
        return f"An error occurred while searching for relevant information: {str(e)}"