from server.db import DataBase
from logging import getLogger
import pickle
logger = getLogger(__name__)

class ActionProcessor:
    def __init__(self):
        self.database = DataBase()
        self.actions = {
            "REGISTER_USER": self.register_user,
        }

    def process(self, action, data):
        action_type = action['type']
        action = self.get_callback(action_type)
        if action:
            logger.info(f"Running action with type: {action_type}")
            action(data)

    def get_callback(self, action_type):
        if action_type in self.actions:
            return self.actions[action_type]
        else:
            logger.error(f"Unknown action: {action_type}")
            return None

    def register_user(self, data):
        logger.info("Start register user...")
        self.database.register_user(**data)

