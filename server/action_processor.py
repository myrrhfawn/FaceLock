from db import DataBase
from logging import getLogger
import pickle

logger = getLogger(__name__)


class ActionProcessor:
    def __init__(self):
        self.database = DataBase()
        self.actions = {
            "REGISTER_USER": self.register_user,
            "GET_ENCODINGS": self.get_encodings,
        }

    def process(self, action, data=None):
        action_type = action["type"]
        action = self.get_callback(action_type)
        if action:
            logger.info(f"Running action with type: {action_type}")
            response = action(data)
            if response:
                return response
        return None

    def get_callback(self, action_type):
        if action_type in self.actions:
            return self.actions[action_type]
        else:
            logger.error(f"Unknown action: {action_type}")
            return None

    def register_user(self, data):
        logger.info("Start register user...")
        self.database.register_user(**data)

    def get_encodings(self, data=None):
        logger.info("Start fetching data from DB...")
        return {"users": self.database.get_all_encode_data()}
