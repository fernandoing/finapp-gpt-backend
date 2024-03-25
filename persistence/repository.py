from abc import ABC, abstractmethod


class Repository(ABC):
    @abstractmethod
    def __init__(self, db_uri: str):
        self._db_uri = db_uri

    @abstractmethod
    def get(self, key: str):
        pass

    @abstractmethod
    def get_by_id(self, key: str, id):
        pass


class BasicRepository(ABC):
    @abstractmethod
    def __init__(self, db_uri: str):
        self._db_uri = db_uri

    @abstractmethod
    def get(self, key: str):
        pass

    @abstractmethod
    def add(self, key: str, value):
        pass


class WriteRepository(ABC):
    @abstractmethod
    def __init__(self, db_uri: str):
        self._db_uri = db_uri

    @abstractmethod
    def add(self, key: str, value):
        pass

    @abstractmethod
    def update(self, key: str, id, value):
        pass

    @abstractmethod
    def delete(self, key: str, id):
        pass


class FullRepository(Repository, WriteRepository):
    @abstractmethod
    def __init__(self, db_uri: str):
        self._db_uri = db_uri

