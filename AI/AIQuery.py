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
requirements_collection = db["Documents.Requirements"]

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
        prompt: The user's query
        document: Relevant document information retrieved from the database
        user_major: The user's major if available
    
    Returns:
        AI-generated response text
    """
    load_dotenv()
    
    # Get relevant documents if none provided
    if not document:
        document = get_relevant_document(prompt, user_major)
    
    # Construct system prompt with retrieved document
    system_content = "You are an advisor for Case Western Reserve University. Your goal is to help the user answer questions about courses and graduation requirements for their major."
    
    if user_major:
        system_content += f" The user's major is {user_major}."
    
    if document:
        system_content += "\n\nBased on the available information, here are the relevant details:\n\n" + document
    else:
        system_content += "\n\nI don't have specific information about that in my database."
    
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

def get_major_requirements(major):
    """
    Retrieve requirements for a specific major from the database.
    
    Args:
        major: The user's declared major
    
    Returns:
        Formatted string containing major requirements
    """
    try:
        # Look up the major in the requirements collection
        major_doc = requirements_collection.find_one(
            {"major": {"$regex": major, "$options": "i"}},
            {"_id": 0}
        )
        
        if not major_doc:
            return None
        
        # Format the major requirements
        formatted_requirements = f"Requirements for {major_doc.get('major', 'Unknown Major')}:\n\n"
        
        # Add core requirements
        if 'core_requirements' in major_doc:
            formatted_requirements += "Core Requirements:\n"
            for course in major_doc['core_requirements']:
                formatted_requirements += f"- {course}\n"
            formatted_requirements += "\n"
        
        # Add elective requirements
        if 'elective_requirements' in major_doc:
            formatted_requirements += "Elective Requirements:\n"
            formatted_requirements += f"{major_doc['elective_requirements']}\n\n"
        
        # Add other requirements
        if 'additional_requirements' in major_doc:
            formatted_requirements += "Additional Requirements:\n"
            formatted_requirements += f"{major_doc['additional_requirements']}\n\n"
        
        return formatted_requirements
    
    except Exception as e:
        print(f"Error retrieving major requirements: {str(e)}")
        return None

def get_relevant_document(prompt, user_major=None):
    """
    Creates an embedding for the user prompt and uses vector search to find relevant documents.
    Also incorporates major requirements if available.
    
    Args:
        prompt: The user's query
        user_major: The user's major if available
    
    Returns:
        Formatted string containing relevant information
    """
    try:
        final_document = ""
        
        # First, get major requirements if available
        if user_major:
            major_requirements = get_major_requirements(user_major)
            if major_requirements:
                final_document += major_requirements + "\n\n"
        
        # Generate embedding for the user's prompt
        query_vector = get_embedding(prompt)
        
        # Perform vector search in MongoDB
        results = courses_collection.aggregate([
            {
                "$vectorSearch": {
                    "index": "vector_index",
                    "path": "embedding",    # Assuming the embedding field is called "embedding"
                    "queryVector": query_vector,
                    "numCandidates": 100,
                    "limit": 5
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
        
        if not final_document:
            return "I couldn't find specific information related to your question in the database."
        
        return final_document
        
    except Exception as e:
        print(f"Error in vector search: {str(e)}")
        return f"An error occurred while searching for relevant information: {str(e)}"


