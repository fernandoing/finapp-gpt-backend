from .repository import Repository
from .repository import BasicRepository
from .repository import FullRepository

import requests


class LoadChatRepository(BasicRepository):
    def __init__(self, db_uri: str):
        super().__init__(db_uri)

    def get(self, key: str):
        headers = {
            "Content-Type": "application/json",
        }

        if key is not None:
            headers["Authorization"] = key

        response = requests.get(
            url=self._db_uri + f"/chat_history",
            headers=headers
        )
        if response.status_code != 200:
            return None
        return response.json()

    def add(self, key: str, value):
        headers = {
            "Content-Type": "application/json",
        }

        if key is not None:
            headers["Authorization"] = key

        response = requests.post(
            url=self._db_uri + f"/chat_history",
            headers=headers,
            json=value
        )
        if response.status_code != 200:
            return None
        return response.json()


class CatgeoryRepository(Repository):
    def __init__(self, db_uri: str):
        super().__init__(db_uri)

    def get(self, key: str):
        headers = {
            "Content-Type": "application/json",
        }

        if key is not None:
            headers["Authorization"] = key

        response = requests.get(
            url=self._db_uri + f"/expense_categories",
            headers=headers
        )
        if response.status_code != 200:
            return None

        categories = response.json().get('categories')
        return response.json()

    def get_by_id(self, key: str, id):
        headers = {
            "Content-Type": "application/json",
        }

        if key is not None:
            headers["Authorization"] = key

        response = requests.get(
            url=self._db_uri + f"/expense_categories/{id}",
            headers=headers
        )
        if response.status_code != 200:
            return None
        return response.json()


class ExpenseRepository(FullRepository):
    def __init__(self, db_uri: str):
        super().__init__(db_uri)

    def add(self, key: str, value):
        headers = {
            "Content-Type": "application/json",
        }

        if key is not None:
            headers["Authorization"] = key

        response = requests.post(
            url=self._db_uri + f"/expenses",
            headers=headers,
            json=value,
        )

        if response.status_code != 201:
            return None

        return response.json()

    def get(self, key: str):
        headers = {
            "Content-Type": "application/json",
        }

        if key is not None:
            headers["Authorization"] = key

        response = requests.get(
            url=self._db_uri + f"/expenses",
            headers=headers
        )
        if response.status_code != 200:
            return None
        expenses = response.json().get('expenses')

        return expenses

    def get_by_id(self, key: str, id):
        headers = {
            "Content-Type": "application/json",
        }

        if key is not None:
            headers["Authorization"] = key

        response = requests.get(
            url=self._db_uri + f"/expenses/{id}",
            headers=headers
        )
        if response.status_code != 200:
            return None
        return response.json()

    def update(self, key: str, id, value):
        headers = {
            "Content-Type": "application/json",
        }

        if key is not None:
            headers["Authorization"] = key

        response = requests.put(
            url=self._db_uri + f"/expenses/{id}",
            headers=headers,
            json=value
        )

        if response.status_code != 200:
            return None

        return response.json().get('updated')

    def delete(self, key: str, id):
        headers = {
            "Content-Type": "application/json",
        }

        if key is not None:
            headers["Authorization"] = key

        response = requests.delete(
            url=self._db_uri + f"/expenses/{id}",
            headers=headers
        )
        if response.status_code != 200:
            return None
        return response.json().get('deleted')

