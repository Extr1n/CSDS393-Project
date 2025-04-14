from pymongo import MongoClient
import ssl
import os
from dotenv import load_dotenv

load_dotenv()  

#TEST DB CONNECTION- not actually needed 
MONGO_URI = os.getenv("DB_key")

try:
    print("Attempting to connect to MongoDB...")
    client = MongoClient(
        MONGO_URI,
        tls=True,
        tlsAllowInvalidCertificates=True  
    )
    
    client.admin.command('ping')
    print("Successfully connected to MongoDB!")
    
    db = client.cluster0
    courses_collection = db["Documents.Courses"]
    user_courses_collection = db.user_courses
    
    print("Available collections:", db.list_collection_names())
    print(f"Documents.Courses count: {courses_collection.count_documents({})}")

except Exception as e:
    print("Failed to connect to MongoDB:")
    print(e)
