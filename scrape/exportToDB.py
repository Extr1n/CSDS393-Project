import json
import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

# Load the contents of allcourse.json
with open('./scrape/parsed_courses.json') as f:
    data = json.load(f)

# Connect to your MongoDB database
client = MongoClient(os.getenv('MONGODB_URI'))
db = client['Documents']
collection = db['Courses']

# Insert the contents of allcourse.json into the database
collection.insert_many(data)