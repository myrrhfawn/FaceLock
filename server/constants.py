from enum import Enum


class StatusCode(Enum):
    SUCCESS = 200


# Connection
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 9000

DEFAULT_BUFFER_SIZE = 8192
HANDLER_TIMEOUT = 30

# Threading
NUMBER_OF_THREADS = 10

# Database
# TODO move to .env file
DB_NAME = "postgres"
DB_USER = "admin"
DB_HOST = "database"
DB_PORT = "5432"
DB_PASSWORD = "12345"
