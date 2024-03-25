from services import GPTService, ExpenseService, ChatService
from services import LoadChatService, GetChatHistoryService, ExpenseManager
from persistence import Repository, WriteRepository
from persistence import LoadChatRepository, CatgeoryRepository, ExpenseRepository

from flask_injector import Binder, request as scope_request, singleton
from dotenv import load_dotenv

import os


load_dotenv()


def configure(binder: Binder):
    API_KEY = os.getenv('OPENAI_API_KEY')
    URI = os.getenv('EXTERNAL_API_URL')
    binder.bind(
        LoadChatService,
        to=GetChatHistoryService(
            LoadChatRepository(db_uri=URI)
        ),
        scope=scope_request
    )
    binder.bind(
        ExpenseService,
        to=ExpenseManager(
            cat_repo=CatgeoryRepository(db_uri=URI),
            exp_repo=ExpenseRepository(db_uri=URI),
            gpt=ChatService(api_key=API_KEY),
            load_chat=GetChatHistoryService(
                LoadChatRepository(db_uri=URI)
            )
        ),
        scope=scope_request
    )

