from logging import getLogger

from db import DataBase

logger = getLogger(__name__)


class ActionProcessor:
    def __init__(self):
        self.database = DataBase()
        self.actions = {
            "REGISTER_USER": self.register_user,
            "GET_ENCODINGS": self.get_encodings,
            "GET_USER": self.get_user,
        }

    def process(self, action, data=None):
        """Process the action based on its type and data."""
        action_type = action["type"]
        action = self.get_callback(action_type)
        if action:
            logger.info(f"Running action with type: {action_type}")
            response = action(data)
            if response:
                return response
        return None

    def get_callback(self, action_type):
        """Get the callback function for the given action type."""
        if action_type in self.actions:
            return self.actions[action_type]
        else:
            logger.error(f"Unknown action: {action_type}")
            return None

    def register_user(self, data):
        """Register a new user in the database."""
        logger.info("Start register user...")
        return self.database.register_user(**data)

    def get_encodings(self, data=None):
        """Fetch all user encodings from the database."""
        logger.info("Start fetching data from DB...")
        return {"users": self.database.get_all_encode_data()}

    def get_user(self, data):
        """Fetch user data by username from the database."""
        logger.info("Start fetching user from DB...")
        username = data.get("username")
        if not username:
            logger.error("Username is required to fetch user data.")
            return None
        user_data = self.database.get_user_by_username(username)
        if user_data:
            return user_data
        else:
            logger.warning(f"User {username} not found.")
            return None
