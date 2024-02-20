from flask import Flask, render_template, request
from chatbot_prototype import StudyChatBot

app = Flask(__name__)

chatbot = StudyChatBot()

def chatbot_response(question):
    return chatbot.query(question)["answer"]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    question = request.form['question']
    answer = chatbot_response(question)
    return answer

if __name__ == '__main__':
    app.run(debug=True)
