from flask import Flask, render_template, request, redirect, url_for, session
from flask_session import Session
from pymongo import MongoClient
from AI.AIQuery import get_response
import random, threading, webbrowser

port = 5000 
url = "http://127.0.0.1:{0}".format(port)

app = Flask(__name__)
app.secret_key = b'hello'

app.config["SESSION_PERMANENT"] = False  
app.config["SESSION_TYPE"] = "filesystem" 
Session(app)

client = MongoClient('localhost', 27017)

db = client.flask_db

threading.Timer(1.25, lambda: webbrowser.open(url) ).start()

@app.route('/')
def index():
    if not session.get("name"):
        return redirect("/login")
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    user_input = request.form.get('question')  # Ensure it matches the form field name

    print("Received user input:", user_input)  # Debugging output

    if not user_input or user_input.strip() == "":  # Handle empty input
        return redirect(url_for('index'))  # Redirect back to input page

    session['user_input'] = user_input
    
    # Debugging output before calling get_response()
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
    # Retrieve user input from session
    user_input = session.get('user_input', None)
    chat = session.get('chat_completion')

    # Pass to template
    return render_template('return.html', user_input=user_input, chat_completion=chat)

if __name__ == '__main__':
    app.run(port=5000, debug=True)
