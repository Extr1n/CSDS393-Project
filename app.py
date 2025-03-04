from flask import Flask, render_template, request, redirect, url_for, session
from AI.AIQuery import get_response

app = Flask(__name__)
app.secret_key = b'hello'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    # Get user input from form
    user_input = request.form.get('user_input')
    
    # Store in session
    session['user_input'] = user_input

    session['chat_completion'] = get_response(user_input, "")
    
    # Redirect to result page
    return redirect(url_for('result'))

@app.route('/result')
def result():
    # Retrieve user input from session
    user_input = session.get('user_input', None)
    
    chat = session.get('chat_completion')

    # Pass to template
    return render_template('return.html', user_input=chat)

if __name__ == '__main__':
    app.run(debug=True)
