from openai import OpenAI
from .service import GPTService
from .service import LoadChatService
from .service import ExpenseService
from persistence import FullRepository, Repository, BasicRepository
from prompts import *

import json
import datetime


class ChatService(GPTService):
    def __init__(self, api_key):
        self._api_key = api_key
        self._client = OpenAI(api_key=self._api_key)

    def ask(self,
            conversation: list,
            instructions: str = DEFAULT_PROMPT,
            model: str = "gpt-3.5-turbo",
            temp: float = 0.7):
        conversation.insert(0, {'role': 'system', 'content': instructions})
        try:
            ai_response = self._client.chat.completions.create(
                messages=conversation,
                model=model,
                temperature=temp
            )
            return ai_response.choices[0].message.content
        except Exception as e:
            print(e.message)
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

    def process_user_input(self, user_input: dict, token) -> int:
        response = self._gpt.ask(
            conversation=[user_input],
            instructions=DETERMINE_INTENT,
            temp=0.3
        )

        if not self._validate_intent(response):
            return -1
        return int(response)

    def user_add_expense(self, user_input: dict, token: str) -> dict:
        list_categories = self._cat_repo.get(key=None)
        conversation = self._load_chat.load(key=token)
        conversation.append(user_input)

        gpt_answer = self._gpt.ask(
            conversation=conversation,
            instructions=ADD_EXPENSE.format(categories=list_categories, date=datetime.date.today()),
            temp=0.5
        )

        if not self._validate_payload(gpt_answer):
            self._save_chat_history(message=user_input, response=gpt_answer, token=token)
            return {'response': gpt_answer}

        print(gpt_answer)
        response: dict = json.loads(gpt_answer)
        message = response.get('message')
        expense = response
        del expense['message']
        print(expense)
        print(message)

        if not self._validate_expense(expense):
            return {'response': 'Something went wrong while adding the expense. Please try again later.'}

        status = self._exp_repo.add(key=token, value=expense)
        print(status)

        if status is None:
            return {'response': 'An error occurred while adding the expense.'}

        self._save_chat_history(message=user_input, response=message, token=token)
        return {'response': message}

    def user_view_expenses(self, user_input: dict, token: str) -> dict:
        expenses = self._exp_repo.get(key=token)

        if expenses is None:
            return {'response': 'An error occurred while fetching the expenses.'}

        response = self._gpt.ask(
            conversation=[{'role': 'user', 'content': json.dumps(expenses)}],
            instructions=STRUCTURE_EXPENSES,
        )

        self._save_chat_history(message=user_input, response=response, token=token)
        return {'response': response}

    def user_general_talk(self, user_input: dict, token: str) -> str:
        categories = self._cat_repo.get(key=None)
        conversation = self._load_chat.load(key=token)
        conversation.append(user_input)

        response = self._gpt.ask(
            conversation=conversation,
            instructions=BASE_PROMPT.format(categories=categories),
            temp=0.7
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

    def _validate_payload(self, response: str) -> bool:
        try:
            _ = json.loads(response)
            return True
        except json.JSONDecodeError:
            return False
        return False

    def _validate_expense(self, payload: dict) -> bool:
        all_keys = {'exp_category_id', 'expense_amount', 'month_year', 'expense_name'}
        return all(k in payload.keys() for k in all_keys)

    def _save_chat_history(self, message: dict, response: str, token: str) -> bool:
        chat = [message]
        chat.append({'role': 'assistant', 'content': response})
        chats_saved = self._load_chat.save(key=token, value=chat)
        return chats_saved > 0

