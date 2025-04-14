from dotenv import load_dotenv
from pymongo import MongoClient
import os
from AI.Embeddings import get_embedding
import time

def index_courses():
    """
    Generate and store embeddings for all courses in the database.
    This should be run once to initialize the vector database.
    """
    load_dotenv()
    
    # Connect to MongoDB
    mongo_client = MongoClient(os.getenv('DB_KEY'))
    db = mongo_client.cluster0
    courses_collection = db["Documents.Courses"]
    
    # Get all courses
    all_courses = list(courses_collection.find({}))
    print(f"Found {len(all_courses)} courses to index.")
    
    # Track progress
    start_time = time.time()
    processed = 0
    
    # Process courses in batches
    batch_size = 50
    for i in range(0, len(all_courses), batch_size):
        batch = all_courses[i:i+batch_size]
        
        # Prepare texts for embedding
        texts = []
        for course in batch:
            # Create comprehensive text representation for each course
            course_text = f"{course.get('code', '')} {course.get('title', '')}: {course.get('description', '')}"
            texts.append(course_text)
        
        # Generate embeddings
        embeddings = get_embedding(texts)
        
        # Update documents with embeddings
        for j, course in enumerate(batch):
            courses_collection.update_one(
                {"_id": course["_id"]},
                {"$set": {"embedding": embeddings[j]}}
            )
        
        processed += len(batch)
        elapsed = time.time() - start_time
        print(f"Processed {processed}/{len(all_courses)} courses ({processed/len(all_courses)*100:.1f}%) in {elapsed:.1f}s")
    
    print(f"Indexing complete! Total time: {time.time() - start_time:.1f} seconds")
    
    # Create vector search index if it doesn't exist
    # Note: This is often done through MongoDB Atlas UI, but can be scripted
    # with the appropriate MongoDB commands
    print("Remember to create a vector search index in MongoDB Atlas if you haven't already.")
    print("Index configuration example:")
    print("""
    {
      "mappings": {
        "dynamic": true,
        "fields": {
          "embedding": {
            "dimensions": 768,
            "similarity": "cosine",
            "type": "knnVector"
          }
        }
      }
    }
    """)

if __name__ == "__main__":
    index_courses()