from abc import ABC, abstractmethod
from persistence import FullRepository
from persistence import BasicRepository


class GPTService(ABC):
    @abstractmethod
    def __init__(self, api_key):
        self._api_key = api_key

    @abstractmethod
    def ask(self,
            conversation: list,
            instructions: str,
            model: str,
            temp: float):
        pass


class LoadChatService(ABC):
    @abstractmethod
    def __init__(self, repository: BasicRepository):
        self._repo = repository

    @abstractmethod
    def load_history(self, key: str):
        pass

    @abstractmethod
    def load(self, key: str):
        pass

    @abstractmethod
    def save(self, key: str, value):
        pass


class ExpenseService(ABC):
    @abstractmethod
    def __init__(self, repository: FullRepository):
        self._repo = repository

    @abstractmethod
    def process_user_input(self, user_input, token) -> int:
        pass

    @abstractmethod
    def user_add_expense(self, user_input, token) -> dict:
        pass

    @abstractmethod
    def user_view_expenses(self, user_input, token) -> dict:
        pass

    @abstractmethod
    def user_general_talk(self, user_input, token) -> str:
        pass

