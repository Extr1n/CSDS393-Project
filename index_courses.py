from dotenv import load_dotenv
from pymongo import MongoClient
import os
from AI.Embeddings import get_embedding
import time

def index_collections():
    """
    Generate and store embeddings for all courses and requirements in the database.
    This should be run once to initialize the vector database.
    """
    load_dotenv()
    
    # Connect to MongoDB
    mongo_client = MongoClient(os.getenv('DB_KEY'))
    db = mongo_client.cluster0
    courses_collection = db["Documents.Courses"]
    requirements_collection = db["Documents.Requirements"]
    
    # Index courses
    print("=== Indexing Courses ===")
    index_collection(courses_collection, "courses")
    
    # Index requirements
    print("\n=== Indexing Requirements ===")
    index_collection(requirements_collection, "requirements")
    
    print("\nIndexing complete! Remember to create vector search indices in MongoDB Atlas.")
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

def index_collection(collection, collection_type):
    """
    Generate and store embeddings for all documents in a collection.
    
    Args:
        collection: MongoDB collection object
        collection_type: String identifier for the collection ('courses' or 'requirements')
    """
    # Get all documents
    all_docs = list(collection.find({}))
    print(f"Found {len(all_docs)} {collection_type} to index.")
    
    if len(all_docs) == 0:
        print(f"No {collection_type} found to index.")
        return
    
    # Track progress
    start_time = time.time()
    processed = 0
    
    # Process documents in batches
    batch_size = 50
    for i in range(0, len(all_docs), batch_size):
        batch = all_docs[i:i+batch_size]
        
        # Prepare texts for embedding
        texts = []
        for doc in batch:
            if collection_type == "courses":
                # For courses: combine code, title and description
                doc_text = f"{doc.get('code', '')} {doc.get('title', '')}: {doc.get('description', '')}"
            else:
                # For requirements: combine major name and requirements
                major = doc.get('major', '')
                core_reqs = ' '.join(doc.get('core_requirements', []))
                elective_reqs = doc.get('elective_requirements', '')
                additional_reqs = doc.get('additional_requirements', '')
                doc_text = f"{major} requirements: {core_reqs} {elective_reqs} {additional_reqs}"
            
            texts.append(doc_text)
        
        # Generate embeddings
        embeddings = get_embedding(texts)
        
        # Update documents with embeddings
        for j, doc in enumerate(batch):
            collection.update_one(
                {"_id": doc["_id"]},
                {"$set": {"embedding": embeddings[j]}}
            )
        
        processed += len(batch)
        elapsed = time.time() - start_time
        print(f"Processed {processed}/{len(all_docs)} {collection_type} ({processed/len(all_docs)*100:.1f}%) in {elapsed:.1f}s")
    
    print(f"{collection_type.capitalize()} indexing complete! Total time: {time.time() - start_time:.1f} seconds")

if __name__ == "__main__":
    index_collections()