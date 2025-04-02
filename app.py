from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_session import Session
from pymongo import MongoClient
from AI.AIQuery import get_response
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
client = MongoClient(os.getenv('DB_key'))
db = client.cluster0
courses_collection = db["Documents.Courses"]
user_courses_collection = db.user_courses

# Test the connection
try:
    # Test the connection by listing collections
    collections = db.list_collection_names()
    print("Connected to MongoDB. Available collections:", collections)
    
    # Test the courses collection
    course_count = courses_collection.count_documents({})
    print(f"Number of courses in database: {course_count}")
except Exception as e:
    print(f"Error connecting to MongoDB: {str(e)}")

threading.Timer(1.25, lambda: webbrowser.open(url) ).start()

@app.route('/')
def index():
    if not session.get("name"):
        return redirect("/login")
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    user_input = request.form.get('question')

    print("Received user input:", user_input)

    if not user_input or user_input.strip() == "":
        return redirect(url_for('index'))

    session['user_input'] = user_input
    
    print("Calling get_response with input:", user_input)

    try:
        session['chat_completion'] = get_response(user_input, "")
    except Exception as e:
        print("Error calling get_response:", str(e))
        session['chat_completion'] = "An error occurred while processing your request."

    return redirect(url_for('result'))

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        session["name"] = request.form.get("name")
        session["caseid"] = request.form.get("caseid")
        session["major"] = request.form.get("major")
        return redirect("/")
    return render_template("login.html")

@app.route('/logout')
def logout():
    session.clear()
    return redirect("/")

@app.route('/chat')
def chat():
    return render_template('chat.html')

@app.route('/result')
def result():
    user_input = session.get('user_input', None)
    chat = session.get('chat_completion')
    return render_template('return.html', user_input=user_input, chat_completion=chat)

@app.route('/course')
def course():
    if not session.get("name"):
        return redirect("/login")
    
    # Get all available courses from Documents.Courses collection
    available_courses = list(courses_collection.find(
        {},
        {"_id": 0}  # Exclude MongoDB _id field
    ))
    
    # Get user's courses
    user_courses = list(user_courses_collection.find(
        {"caseid": session.get("caseid")},
        {"_id": 0}  # Exclude MongoDB _id field
    ))
    
    return render_template('course.html', 
                         available_courses=available_courses,
                         user_courses=user_courses)

@app.route('/search_courses')
def search_courses():
    query = request.args.get('query', '').strip()
    print(f"Searching for courses with query: {query}")  # Debug log
    
    if len(query) < 2:
        print("Query too short, returning empty results")  # Debug log
        return jsonify([])
    
    try:
        # Search in Documents.Courses collection
        courses = list(courses_collection.find(
            {
                "$or": [
                    {"code": {"$regex": query, "$options": "i"}},
                    {"title": {"$regex": query, "$options": "i"}}
                ]
            },
            {"_id": 0}  # Exclude MongoDB _id field
        ).limit(10))  # Limit results to 10 courses
        print(courses)  # Debug log
        
       
        
        
        print(f"Found {len(courses)} courses")  # Debug log
        print(f"Courses: {courses}")  # Debug log
        
        return jsonify(courses)
    except Exception as e:
        print(f"Error searching courses: {str(e)}")  # Debug log
        return jsonify({"error": str(e)}), 500

@app.route('/add_course', methods=['POST'])
def add_course():
    if not session.get("name"):
        print("User not logged in")  # Debug log
        return jsonify({"error": "Not logged in"}), 401
    
    try:
        course_data = request.get_json()
        print(f"Received course data: {course_data}")  # Debug log
        
        # Validate required fields
        required_fields = ['code', 'title', 'credits']
        for field in required_fields:
            if field not in course_data:
                print(f"Missing required field: {field}")  # Debug log
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Add user's caseid to the course data
        course_data["caseid"] = session.get("caseid")
        course_data["status"] = "Planned"  # Default status for new courses
        
        print(f"Course data with user info: {course_data}")  # Debug log
        
        # Check if course already exists for user
        existing_course = user_courses_collection.find_one({
            "caseid": session.get("caseid"),
            "code": course_data["code"]
        })
        
        if existing_course:
            print(f"Course already exists: {course_data['code']}")  # Debug log
            return jsonify({"error": "Course already exists in your list"}), 400
        
        # Add course to user's courses
        result = user_courses_collection.insert_one(course_data)
        print(f"Course added successfully: {result.inserted_id}")  # Debug log
        
        return jsonify({
            "message": "Course added successfully",
            "refresh": True
        }), 200
        
    except Exception as e:
        print(f"Error adding course: {str(e)}")  # Debug log
        return jsonify({"error": str(e)}), 500

@app.route('/init_db')
def init_db():
    try:
        # Connect to the actual MongoDB database
        client = MongoClient(os.getenv('DB_key'))
        db = client["Documents"]
        collection = db["Courses"]
        
        # Get all courses, excluding the _id field
        raw_courses = list(collection.find({}, {"_id": 0}))
        
        if not raw_courses:
            return jsonify({
                "error": "No courses found in Documents.Courses",
                "details": "The collection is empty"
            })
        
        # Transform the courses to match our format
        transformed_courses = []
        for course in raw_courses:
            transformed_course = {
                "code": course.get('class_code', ''),  # Map class_code to code
                "title": course.get('class_title', ''),  # Map class_title to title
                "credits": course.get('units', '').split()[0],  # Extract number from "3 Units"
                "department": course.get('department', ''),
                "description": course.get('description', '')
            }
            transformed_courses.append(transformed_course)
        
        # Clear existing courses in our collection
        courses_collection.delete_many({})
        
        # Insert the transformed courses into our collection
        courses_collection.insert_many(transformed_courses)
        
        # Get a sample course for the response
        sample_course = transformed_courses[0] if transformed_courses else None
        
        return jsonify({
            "message": f"Successfully imported {len(transformed_courses)} courses from Documents.Courses",
            "sample_course": sample_course,
            "total_courses": len(transformed_courses)
        })
            
    except Exception as e:
        print(f"Error initializing database: {str(e)}")
        return jsonify({
            "error": str(e),
            "details": "Check the server console for more information"
        }), 500

@app.route('/delete_course', methods=['POST'])
def delete_course():
    if not session.get("name"):
        return jsonify({"error": "Not logged in"}), 401
    
    try:
        data = request.get_json()
        course_code = data.get('code')
        
        if not course_code:
            return jsonify({"error": "Course code is required"}), 400
        
        # Delete the course from user's courses
        result = user_courses_collection.delete_one({
            "caseid": session.get("caseid"),
            "code": course_code
        })
        
        if result.deleted_count == 0:
            return jsonify({"error": "Course not found"}), 404
        
        return jsonify({"message": "Course deleted successfully"}), 200
        
    except Exception as e:
        print(f"Error deleting course: {str(e)}")  # Debug log
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)
