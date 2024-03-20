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

app = Flask(__name__)
CORS(app)

def chat_with_gpt_for_expenses(user_input):
    prompt = prompts.add_expense.format(user_input=user_input,json_example=prompts.json_example)
    response = chat_with_gpt(prompt)
    try:
        # Assuming GPT might structure the output correctly based on the prompt's guidance
        expense_details = json.loads(response)
        if 'expense_name' in expense_details:
            return expense_details
        else:
            return {}
    except json.JSONDecodeError:
        return {}

def add_expense(expense_data):
    response = requests.post(f"{EXTERNAL_API_URL}/expenses", json={"expense": expense_data})
    if response.status_code != 200:
        return {"error": f"API call failed with status code {response.status_code}", "details": response.text}
    return response.json()

@app.route('/get_response', methods=['POST'])
def get_response():
    data = request.get_json()
    user_input = data['user_input']

    # First, let's use GPT to understand if this is an expense-related query or general financial advice.
    # This example assumes you have trained or fine-tuned GPT to respond accordingly.

    prompt = prompts.determine_intent.format(user_input=user_input)
    test = prompts.expense_added.format(user_input=user_input)
    intent = chat_with_gpt(prompt)
    if "1" in intent:
        # Specific trigger or keyword based on GPT's response indicating an expense is to be added.
        expense_details = chat_with_gpt_for_expenses(user_input)
        if expense_details:
            expense_response = add_expense(expense_details)
            prompt = prompts.expense_added.format(user_input=expense_details)
            print(prompt)
            if not "error" in expense_response:
                response = chat_with_gpt(prompt)
                return jsonify({'response': response})
            response = chat_with_gpt(prompts.expense_added)
            return jsonify({'response': response})
        else:
            response = chat_with_gpt(prompts.unclear_expense)
            return jsonify({'response': response})
    else:
        # For all other inquiries, return a general response.
        # This could include financial advice or answers to specific questions.
        general_response = chat_with_gpt(user_input)
        return jsonify({'response': general_response})
    
def chat_with_gpt(prompt, model="gpt-3.5-turbo"):
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": prompts.base_prompt},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(e)

if __name__ == '__main__':
    app.run(debug=True)