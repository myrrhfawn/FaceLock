import json
import logging
from datetime import datetime
from urllib.parse import quote

from sqlalchemy import Column, DateTime, Integer, String, LargeBinary, create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from fl_utils.base_logging import setup_logging
from server.constants import DB_NAME, DB_USER, DB_HOST, DB_PORT, DB_PASSWORD
Base = declarative_base()
setup_logging(file_name="db.log")

logger = logging.getLogger(__name__)

class User(Base):
    """Represents a training table in the database with relevant details like project ID, type, and training status."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(255))
    password = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    encode_data = Column(LargeBinary)

    def __str__(self):
        return (
            f"User [ID: {self.id}, username: {self.username}, created_at: {self.created_at} ]"
        )

    def __repr__(self):
        return (
            f"User [ID: {self.id}, username: {self.username}, created_at: {self.created_at} ]"
        )

class DataBase:
    """Handles database operations: creating tables, adding, updating, and deleting training and inference requests."""
    def __init__(self):
        """Initialize the database connection with predefined configuration."""
        self.dbname = DB_NAME
        self.user = DB_USER
        self.port = DB_PORT
        self.host = DB_HOST
        self.db_url = (
            f"postgresql+psycopg2://{self.user}:{quote(DB_PASSWORD)}@{self.host}:{self.port}/{self.dbname}"
        )
        # TODO: configure reconnect
        self.engine = create_engine(
            self.db_url,
            pool_pre_ping=True,  # Enables a pre-ping to test the connection
            pool_recycle=60 * 30,  # Reconnect each 30 min
        )
        self.Session = sessionmaker(bind=self.engine)



    def register_user(self, username, password, encode_data=None):
        session = self.Session()
        try:
            logger.info("Adding new user into DB.")
            user = User(username=username, password=password, encode_data=encode_data)
            session.add(user)
            session.commit()
            logger.info(f"Added user with username: {username}")

        except Exception as e:
            session.rollback()
            logger.exception(e)
        finally:
            session.close()

    def check_and_create_tables(self):
        """Creates necessary tables in the database if they do not already exist."""
        logger.info("Creating tables using SQLAlchemy")
        Base.metadata.create_all(self.engine)
    def drop_user_table(self):
        """Drops the train request table from the database."""
        engine = self.engine
        try:
            User.__table__.drop(engine)
            return True

        except Exception as e:
            logger.error(f"Error deleting User table {e}")
            return False

    def get_all_encode_data(self):
        session = self.Session()
        try:
            users = session.query(User.username, User.encode_data).all()
            data_list = [{"username": username, "encode_data": encoding} for username, encoding in users]
            return data_list
        except Exception as e:
            print(f"Error occurred: {e}")
            return None
        finally:
            session.close()


if __name__ == "__main__":
    database = DataBase()
    database.check_and_create_tables()
