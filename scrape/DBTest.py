import os
from dotenv import load_dotenv
from langchain_community.document_loaders.mongodb import MongodbLoader
import nest_asyncio

nest_asyncio.apply()
load_dotenv()
loader = MongodbLoader(
    connection_string=os.environ['MONGODB_URI'],
    db_name=os.environ['MONGODB_DB'],
    collection_name=os.environ['MONGODB_COLL'],
    filter_criteria={},
    field_names=["title", "plot"]
)
docs = loader.load()

print(len(docs))
docs[0]