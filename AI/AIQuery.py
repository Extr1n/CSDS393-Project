"""
CWRU Course Advisor AI Module.

This module provides functionality for retrieving and providing information about
courses and graduation requirements at Case Western Reserve University using
AI-powered responses and vector search.

Functions:
    get_response: Generate AI responses based on user prompts and relevant course data.
    get_major_requirements: Retrieve requirements for a specific major.
    get_relevant_document: Retrieve relevant course information based on user queries.
"""

from dotenv import load_dotenv
from groq import Groq
from pymongo import MongoClient
import os
from AI.Embeddings import get_embedding

load_dotenv()

client = Groq()

# Connect to MongoDB using your connection string.
# The database is "cluster0" with two separate collections for course metadata and embeddings,
# and one for requirements.
mongo_client = MongoClient(os.getenv('DB_KEY'))
db = mongo_client["cluster0"]

# Collections for course metadata and requirements (stored in Documents/courses and Documents/requirements)
courses_meta_collection = mongo_client["Documents"]["Courses"]
requirements_collection = mongo_client["Documents"]["Requirements"]

# Collection with course embeddings (vector index is built on this collection)
courses_embeddings_collection = mongo_client["cluster0"]["Documents.Courses"]

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

def get_response(prompt, document=None, user_major=None):
    """
    Generate an AI response based on the user prompt and relevant documents.
    
    Uses the Groq API with the llama-3.3-70b-versatile model to generate responses
    that help CWRU students with questions about courses and major requirements.
    
    Args:
        prompt (str): The user's query about courses or requirements.
        document (str, optional): Relevant document information retrieved from the database.
            If None, the function will attempt to retrieve relevant documents automatically.
        user_major (str, optional): The user's major if available, used to provide
            more targeted responses about major requirements.
    
    Returns:
        str: AI-generated response text answering the user's query.
    
    Example:
        >>> response = get_response("What courses do I need for a Computer Science major?", 
                                   user_major="Computer Science")
        >>> print(response)
        "To complete a Computer Science major at CWRU, you'll need the following courses..."
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
    
    Searches the requirements collection in MongoDB for the specified major
    and formats the requirements into a human-readable string.
    
    Args:
        major (str): The user's declared major (case-insensitive search is performed).
    
    Returns:
        str or None: A formatted string containing major requirements including 
            credit hours, required courses, and elective courses. Returns None if the
            major is not found or if an error occurs.
    
    Example:
        >>> requirements = get_major_requirements("Computer Science")
        >>> print(requirements)
        "Requirements for Computer Science:
        
        Credit Hours Required: 120
        
        Required Courses:
        - CSDS 132: Introduction to Programming in Java
        - CSDS 233: Data Structures
        ..."
    """
    try:
        # Perform a search for the major in the requirements collection
        # Use the array element match since title is stored as an array
        major_doc = requirements_collection.find_one(
            {"title.0": {"$regex": major, "$options": "i"}},
            {"_id": 0}
        )
        
        if not major_doc:
            return None
        
        # Get the actual major title from the array
        major_title = major_doc.get('title', ['Unknown Major'])[0]
        formatted_requirements = f"Requirements for {major_title}:\n\n"
        
        # Include credit hour requirements if available
        if 'credit hours' in major_doc and major_doc['credit hours']:
            credit_hours = major_doc['credit hours'][0]
            formatted_requirements += f"Credit Hours Required: {credit_hours}\n\n"
        
        # Include required courses if available
        if 'necessary' in major_doc and major_doc['necessary']:
            formatted_requirements += "Required Courses:\n"
            for course_array in major_doc['necessary']:
                if course_array and len(course_array) > 0:
                    formatted_requirements += f"- {course_array[0]}\n"
            formatted_requirements += "\n"
        
        # Include elective courses if available
        if 'electives' in major_doc and major_doc['electives']:
            formatted_requirements += "Elective Courses:\n"
            for elective in major_doc['electives']:
                formatted_requirements += f"- {elective}\n"
            formatted_requirements += "\n"
        
        return formatted_requirements
    
    except Exception as e:
        print(f"Error retrieving major requirements: {str(e)}")
        return None

def get_relevant_document(prompt, user_major=None):
    """
    Retrieve relevant course information based on semantic similarity to the user query.
    
    Uses vector embeddings to perform a semantic search in the courses database and
    also incorporates major requirements if available.
    
    Args:
        prompt (str): The user's query about courses or requirements.
        user_major (str, optional): The user's declared major, used to include
            major-specific requirements in the response.
    
    Returns:
        str: A formatted document containing relevant course information and/or
            major requirements.
    
    Example:
        >>> result = get_relevant_document("Tell me about machine learning courses", 
                                          user_major="Computer Science")
        >>> print(result)
        "Requirements for Computer Science:
        ...
        
        Here are some relevant courses that might answer your question:
        
        Course: CSDS 440 - Machine Learning
        Credits: 3
        Department: Computer Science
        Description: This course covers fundamental concepts in machine learning..."
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
                    "index": "cool_index",
                    "path": "embedding",    # Assuming the embedding field is called "embedding"
                    "queryVector": query_vector,
                    "numCandidates": 100,
                    "limit": 5,
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

        print(courses_embeddings_collection.find_one())
        
        results = list(courses_embeddings_collection.aggregate(pipeline))
        
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