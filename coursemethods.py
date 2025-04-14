from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_session import Session
from pymongo import MongoClient

import random, threading, webbrowser
import os
from dotenv import load_dotenv


load_dotenv()

port = 5000 
url = "http://127.0.0.1:{0}".format(port)

app = Flask(__name__)
app.secret_key = b'hello'

app.config["SESSION_PERMANENT"] = False  
app.config["SESSION_TYPE"] = "filesystem" 
Session(app)

# MongoDB connection
client = MongoClient(os.getenv('DB_KEY'))
db = client.cluster0
courses_collection = db["Documents.Courses"]
user_courses_collection = db.user_courses


def delete_course(user_courses_collection,user, code):

    
    try:

  
        result = user_courses_collection.delete_one({
            "caseid": user,
            "code": code
        })
        
        if result.deleted_count == 0:
            return jsonify({"error": "Course not found"}), 404
        
        return jsonify({"message": "Course deleted successfully"}), 200
        
    except Exception as e:
        print(f"Error deleting course: {str(e)}")  # Debug log
        return jsonify({"error": str(e)}), 500
    
    
delete_course(user_courses_collection,"dd","CSDS 281")