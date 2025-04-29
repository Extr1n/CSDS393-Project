"""Import course requirement data from a JSON file into MongoDB.

This script loads course requirement data from a JSON file and imports it into
a MongoDB collection. It uses environment variables for database connection
parameters.

Example:
    $ python exportToDB.py

Environment Variables:
    MONGODB_URI: The MongoDB connection string URI.

File Dependencies:
    ./scrape/req/test.json: JSON file containing course requirement data to be 
    imported into the database.
"""

import json
import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

# Load the contents of allcourse.json
with open('./scrape/req/test.json') as f:
    data = json.load(f)

# Connect to your MongoDB database
client = MongoClient(os.getenv('MONGODB_URI'))
db = client['Documents']
collection = db['Requirements']

# Insert the contents of allcourse.json into the database
collection.insert_many(data)