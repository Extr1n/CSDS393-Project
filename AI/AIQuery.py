from dotenv import load_dotenv
from groq import Groq
from pymongo import MongoClient
import os
from Embeddings import get_embedding
import numpy as np 

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
    """
    try:
        final_document = ""
        
        if user_major:
            major_requirements = get_major_requirements(user_major)
            if major_requirements:
                final_document += major_requirements + "\n\n"
        
        #CRUCIAL EMBEDDING FIXES
        query_vector = get_embedding(prompt)
        
        # Convert numpy array to list if necessary
        if isinstance(query_vector, np.ndarray):
            query_vector = query_vector.tolist()
        
        #Ensure values are Python floats (MongoDB requires 64-bit floats)
        query_vector = [float(val) for val in query_vector]
        
        #Verify vector length matches index dimensions
        if len(query_vector) != 768:
            raise ValueError(f"Embedding dimension mismatch. Expected 768, got {len(query_vector)}")

        pipeline = [
            {
                "$vectorSearch": {
                    "index": "vector_index",
                    "path": "embedding",
                    "queryVector": query_vector,  # 🔧 Now properly formatted
                    "numCandidates": 100,
                    "limit": 5,
                    "filter": {"department": user_major} if user_major else None  # 🔧 Optional filter
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
        ]
        
        #Added explicit timeout and error handling
        try:
            results = list(courses_collection.aggregate(pipeline, maxTimeMS=5000))
        except Exception as agg_error:
            print(f"Aggregation error: {str(agg_error)}")
            return final_document + "\n\nError searching course database."
        
        if not results:
            return final_document or "No relevant courses found."
        
        courses_info = "Relevant courses:\n\n"
        for course in results:
            #Handle potential missing fields
            courses_info += (
                f"Course: {course.get('code', 'N/A')} - {course.get('title', 'No title')}\n"
                f"Credits: {course.get('credits', 'N/A')}\n"  #Fixed typo in 'credits'
                f"Department: {course.get('department', 'N/A')}\n"
                f"Description: {course.get('description', 'No description available')}\n\n"
            )
        
        return final_document + courses_info
        
    except Exception as e:
        print(f"Vector search error: {str(e)}")
        return "Error retrieving information. Please try again later."