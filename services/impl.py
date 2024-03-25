from openai import OpenAI
from .service import GPTService
from .service import LoadChatService
from .service import ExpenseService
from persistence import FullRepository, Repository, BasicRepository
from prompts import *

import json


class ChatService(GPTService):
    def __init__(self, api_key):
        self._api_key = api_key
        self._client = OpenAI(api_key=self._api_key)

    def ask(self, conversation: list, instructions: str = BASE_PROMPT, model: str = "gpt-3.5-turbo"):
        conversation.insert(0, {'role': 'system', 'content': instructions})
        try:
            ai_response = self._client.chat.completions.create(
                messages=conversation,
                model=model
            )
            return ai_response.choices[0].message.content
        except Exception as e:
            return "Something went wrong with the AI. Please try again later."


class GetChatHistoryService(LoadChatService):
    def __init__(self, repository: BasicRepository):
        self._repo = repository

    def load_history(self, key: str):
        data: dict = self._repo.get(key)
        if data is None:
            return []

        chats = []
        for chat in data.get('chats', []):
            c = {
                'isUser': chat['role_id'] == 3,
                'text': chat['content']
            }
            chats.append(c)
        return chats

    def load(self, key: str):
        data: dict = self._repo.get(key)
        if data is None:
            return []

        if len(data.get('chats')) == 0:
            return []

        chats = self._transform_to_get(conversation=data.get('chats'))
        return chats

    def save(self, key: str, value):
        payload = self._transform_to_add(conversation=value)
        status = self._repo.add(key, payload)
        if status is None:
            return 0
        return status.get('chats_added', 0)

    def _transform_to_add(self, conversation: list[dict]) -> dict:
        roles = {
            'system': 1,
            'assistant': 2,
            'user': 3
        }

        chats = []
        for chat in conversation:
            c = {
                'role_id': roles[chat['role']],
                'content': chat['content']
            }
            chats.append(c)
        payload = {
            'chats': chats
        }
        return payload

    def _transform_to_get(self, conversation: list[dict]) -> list[dict]:
        roles = {
            1: 'system',
            2: 'assistant',
            3: 'user'
        }

        chats = []
        for chat in conversation:
            c = {
                'role': roles[chat['role_id']],
                'content': chat['content']
            }
            chats.append(c)
        return chats


class ExpenseManager(ExpenseService):
    def __init__(self, cat_repo: Repository, exp_repo: FullRepository, gpt: GPTService, load_chat: LoadChatService):
        self._cat_repo = cat_repo
        self._exp_repo = exp_repo
        self._gpt = gpt
        self._load_chat = load_chat

    def process_user_input(self, user_input: dict) -> int:
        response = self._gpt.ask(
            conversation=[user_input],
            instructions=DETERMINE_INTENT
        )

        if not self._validate_intent(response):
            return -1
        return int(response)

    def user_add_expense(self, user_input: dict, token: str) -> dict:
        categories = self._cat_repo.get(key=None)
        response = self._gpt.ask(
            conversation=[user_input],
            instructions=ADD_EXPENSE.format(json_example=JSON_EXAMPLE, categories=categories)
        )

        if not self._validate_expense(response):
            ask_more = self._gpt.ask(
                conversation=[user_input],
                instructions=UNCLEAR_EXPENSE
            )
            self._save_chat_history(message=user_input, response=ask_more, token=token)
            return {'response': ask_more}

        status = self._exp_repo.add(key=token, value=json.loads(response))

        if status is None:
            return {'response': 'An error occurred while adding the expense.'}

        success = self._gpt.ask(
            conversation=[user_input],
            instructions=EXPENSE_ADDED
        )

        self._save_chat_history(message=user_input, response=success, token=token)
        return {'response': success}

    def user_view_expenses(self, user_input: dict, token: str) -> dict:
        expenses = self._exp_repo.get(key=token)

        if expenses is None:
            return {'response': 'An error occurred while fetching the expenses.'}

        response = self._gpt.ask(
            conversation=[{'role': 'user', 'content': json.dumps(expenses)}],
            instructions=STRUCTURE_EXPENSES
        )

        self._save_chat_history(message=user_input, response=response, token=token)
        return {'response': response}

    def user_general_talk(self, user_input: dict, token: str) -> str:
        categories = self._cat_repo.get(key=None)
        conversation = self._load_chat.load(key=token)
        conversation.append(user_input)

        response = self._gpt.ask(
            conversation=conversation,
            instructions=BASE_PROMPT.format(categories=categories)
        )

        self._save_chat_history(message=user_input, response=response, token=token)
        return {'response': response}

    def _validate_intent(self, intent: str) -> bool:
        try:
            is_number = int(intent)
            return True
        except ValueError:
            return False
        return False

    def _validate_expense(self, response: str) -> bool:
        try:
            valid_json: dict = json.loads(response)
            all_keys = {'exp_category_id', 'expense_amount', 'month_year', 'expense_name'}
            return all(k in valid_json.keys() for k in all_keys)
        except json.JSONDecodeError:
            return False
        return False

    def _save_chat_history(self, message: dict, response: str, token: str) -> bool:
        chat = [message]
        chat.append({'role': 'assistant', 'content': response})
        chats_saved = self._load_chat.save(key=token, value=chat)
        return chats_saved > 0

