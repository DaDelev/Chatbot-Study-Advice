from flask import Flask, render_template, request
from chatbot_prototype import StudyChatBot

app = Flask(__name__)

chatbot = None

def chatbot_response(question):
    response = chatbot.query(question)
    return response['answer']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/init', methods=['POST'])
def init():
    studyProgram = request.form['studyProgram']
    global chatbot
    chatbot = StudyChatBot(studyProgram)
    return "OK"


@app.route('/ask', methods=['POST'])
def ask():
    question = request.form['question']
    answer = chatbot_response(question)
    return answer

if __name__ == '__main__':
    app.run(debug=True)
