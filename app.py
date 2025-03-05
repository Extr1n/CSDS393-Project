from flask import Flask, render_template, request, redirect, url_for, session
from AI.AIQuery import get_response

app = Flask(__name__)
app.secret_key = b'hello'

@app.route('/')
def index():
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

@app.route('/page2')
def page2():
    return render_template('page2.html')

@app.route('/result')
def result():
    # Retrieve user input from session
    user_input = session.get('user_input', None)
    chat = session.get('chat_completion')

    # Pass to template
    return render_template('return.html', user_input=user_input, chat_completion=chat)

if __name__ == '__main__':
    app.run(debug=True)
