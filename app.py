from flask import Flask, jsonify, request
from flask_injector import inject, FlaskInjector
from flask_cors import CORS
from ioc import configure

from services import LoadChatService
from services import GPTService
from services import ExpenseService

import os

app = Flask(__name__)
CORS(app)


@app.route('/chats', methods=['GET'])
@inject
def chats(service: LoadChatService):
    token = request.headers.get('Authorization')
    data = service.load_history(key=token)
    return jsonify({'chats': data})


@app.route('/message', methods=['POST'])
@inject
def chat(service: ExpenseService):
    token = request.headers.get('Authorization')
    data = request.get_json()
    message = {'role': 'user', 'content': data['user_input']}

    response = ''

    choice = service.process_user_input(message, token)

    if choice == -1:
        return jsonify({'response': 'Something went wrong. Please try again later.'})

    if choice == 1:
        response = service.user_add_expense(user_input=message, token=token)

    if choice == 2:
        response = service.user_view_expenses(user_input=message, token=token)

    if choice == 3:
        response = service.user_general_talk(user_input=message, token=token)

    return jsonify(response)


if __name__ == '__main__':
    FlaskInjector(app=app, modules=[configure])
    app.run(debug=True, host=os.getenv('APP_HOST', '127.0.0.1'))

