from flask import Flask, request, jsonify
import os
import requests
from openai import OpenAI
from dotenv import load_dotenv
from flask_cors import CORS
from datetime import datetime
import prompts
import json

load_dotenv()

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
EXTERNAL_API_URL = os.getenv('EXTERNAL_API_URL')
HEADERS = {"Authorization": os.getenv('AUTHORIZATION')}

app = Flask(__name__)
CORS(app)


def chat_with_gpt_for_expenses(user_input, categories):
    current_date = datetime.now().strftime("%Y-%m-%d")
    prompt = prompts.add_expense.format(
        user_input=user_input, json_example=prompts.json_example, categories=categories, current_date=current_date)
    response = chat_with_gpt(prompt)
    try:
        expense_details = json.loads(response)
        if 'expense_name' in expense_details:
            return expense_details
        else:
            return {}
    except json.JSONDecodeError:
        return {}


def add_expense(expense_data):
    response = requests.post(
        f"{EXTERNAL_API_URL}/expenses", json=expense_data, headers=HEADERS)
    print(response)
    if response.ok:
        return response.json()
    else:
        return {"error": f"API call failed with status code {response.status_code}", "details": response.text}


def get_expenses():
    response = requests.get(f"{EXTERNAL_API_URL}/expenses", headers=HEADERS)
    if response.ok:
        return response.json()
    else:
        return {"error": f"API call failed with status code {response.status_code}", "details": response.text}


def get_categories():
    response = requests.get(
        f"{EXTERNAL_API_URL}/expense_categories", headers=HEADERS)
    if response.ok:
        return response.json()
    else:
        return {"error": f"API call failed with status code {response.status_code}", "details": response.text}


def get_history():
    response = requests.get(
        f"{EXTERNAL_API_URL}/chat_history", headers=HEADERS)
    if response.ok:
        return response.json()
    else:
        return {"error": f"API call failed with status code {response.status_code}", "details": response.text}


def add_history(input):
    response = requests.post(
        f"{EXTERNAL_API_URL}/chat_history", json=input, headers=HEADERS)
    if response.ok:
        return response.json()
    else:
        return {"error": f"API call failed with status code {response.status_code}", "details": response.text}








@app.route('/get_response', methods=['POST'])
def get_response():
    data = request.get_json()
    user_input = data['user_input']
    add_history({"role": 1, "message": user_input})

    prompt = prompts.determine_intent.format(user_input=user_input)
    intent = chat_with_gpt(prompt)
    print(intent)
    response = ""
    if "1" in intent:
        categories = get_categories()
        expense_details = chat_with_gpt_for_expenses(user_input, categories)
        if expense_details:
            print(expense_details)
            expense_response = add_expense(expense_details)
            print(expense_response)
            prompt = prompts.expense_added.format(user_input=expense_details)
            print(prompt)
            if not "error" in expense_response:
                response = chat_with_gpt(prompt)
            else:
                return jsonify({'response': "There was an error adding your expenses. Try again later."})
        else:
            response = chat_with_gpt(prompts.unclear_expense)
    elif "2" in intent:
        expenses = get_expenses()
        prompt = prompts.structure_expenses.format(
            user_input=user_input, expenses=expenses)
        print(prompt)
        if not "error" in expenses:
            response = chat_with_gpt(prompt)
        else:
            return jsonify({'response': "There was an error retrieving your expenses. Try again later."})
    else:
        response = chat_with_gpt(user_input)
    add_history({"role": 2, "message": response})
    print(response)
    return jsonify({'response': response})


def chat_with_gpt(prompt, model="gpt-3.5-turbo"):
    # previous_messages = get_history().get('chat_history')
    # print(previous_messages)
    previous_messages = []
    if previous_messages is None:
        previous_messages = []

    messages = [
        {"role": "system", "content": prompts.base_prompt}
    ] + previous_messages + [
        {"role": "user", "content": prompt}
    ]
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages

        )
        print(response)
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(e)


if __name__ == '__main__':
    app.run(debug=True)
