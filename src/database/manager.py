import os
import sys
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from alembic.config import Config
from alembic import command

from .models import Base, FlashcardSet, Flashcard

root_path = Path(__file__).parent.parent.parent

src_path = root_path / "src"

# see if this src path exists.
# if it does, we are in a container.
# if not, we are in local.
if not src_path.exists():
    raise FileNotFoundError("src path does not exist. are you running this script locally?")

src_path_str = str(src_path)
if src_path_str not in sys.path:
    sys.path.insert(0, src_path_str)

DATABASE_NAME = "flashcards.db"

alembic_cfg_path = root_path / "alembic.ini"

alembic_cfg = Config(alembic_cfg_path)


class DatabaseManager:

    def __init__(self):
        """Initializes the DatabaseManager with an engine."""
        self.engine = create_engine(f"sqlite:///{DATABASE_NAME}")

    def create_session(self):
        """Creates a new session with the bound engine."""
        if not self.engine:
            raise ValueError("Database engine is not initialized.")

        Session = sessionmaker(bind=self.engine)
        return Session()

    @staticmethod
    def ensure_db_upgraded():
        """Ensures that the database is upgraded to the latest version."""
        command.upgrade(alembic_cfg, "head")

    @staticmethod
    def init_db():
        """Initializes the database and creates tables based on models."""
        try:
            engine = create_engine(f"sqlite:///{DATABASE_NAME}")
            Base.metadata.create_all(engine)
        except Exception as e:
            # Log or print the exception for debugging
            print(f"An error occurred while initializing the database: {e}")
            raise e

    @staticmethod
    def flush_data():
        """Removes all data from the database."""
        try:
            engine = create_engine(f"sqlite:///{DATABASE_NAME}")
            with sessionmaker(bind=engine)() as session:
                session.query(FlashcardSet).delete()
                session.query(Flashcard).delete()
                session.commit()
        except Exception as e:
            # Log or print the exception for debugging
            print(f"An error occurred while flushing the database: {e}")
            raise e

    @staticmethod
    def delete_db():
        """Deletes the database."""
        try:
            engine = create_engine(f"sqlite:///{DATABASE_NAME}")
            engine.dispose()
            Base.metadata.drop_all(engine)
            # delete from disk
            if os.path.exists(DATABASE_NAME):
                os.remove(DATABASE_NAME)
        except Exception as e:
            # Log or print the exception for debugging
            print(f"An error occurred while deleting the database: {e}")
            raise e
