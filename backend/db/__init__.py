import os

from sqlalchemy import create_engine

from db.models import Base
from db.models.message import Message
from db.models.conversation import Conversation

current_dir = os.path.dirname(os.path.abspath(__file__))

project_root = os.path.abspath(os.path.join(current_dir, ".."))

db_path = os.path.join(project_root, "db/finance_chat_bot.db")


class DB:
    def __init__(self):
        self._engine = create_engine(f"sqlite:///{db_path}", echo=True)

    def setup_db(self, is_drop_table: bool = False):
        with self._engine.begin() as conn:
            if is_drop_table:
                Base.metadata.drop_all(conn)

            Base.metadata.create_all(conn)

    @property
    def engine(self):
        return self._engine


database = DB()
