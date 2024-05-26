import sys
import pickle
from socketserver import StreamRequestHandler
from server.action_processor import ActionProcessor
from io import BytesIO
from server.constants import DEFAULT_BUFFER_SIZE, HANDLER_TIMEOUT, StatusCode
from logging import getLogger

logger = getLogger(__name__)

class TCPHandler(StreamRequestHandler):
    def __init__(self, *args, **kwargs):
        self.timeout = HANDLER_TIMEOUT
        self.action_processor = ActionProcessor()
        super().__init__(*args, **kwargs)

    def handle(self):
        try:
            buffer = BytesIO()
            ip_address = self.client_address[0]
            logger.info(f"Request from - {ip_address}")
            self.data = self.request.recv(DEFAULT_BUFFER_SIZE)

            buffer.write(self.data)
            #decoded_message = buffer.getvalue().decode(encoding='utf-8', errors='ignore')
            if self.data:
                action = pickle.loads(self.data)
                logger.info(f"action: {action}")
                if not action.get("type"):
                    logger.error(f"Unknown action: {action}")
                    self.send_error("UNKNOWN_ACTION_TYPE")
                if action.get("request") == "GET":
                    response = self.pre_process_get_action(action)
                    self.send_data_to_client(response)
                elif action.get("request") == "POST":
                    self.send_success_message()
                    self.pre_process_post_action(action)
                    self.send_success_message()
            self.request.close()
        except ConnectionResetError:
            logger.warning("Connection Reset")
        except Exception:
            logger.exception("Failed to handle request")
        sys.exit(0)

    def pre_process_post_action(self, action: dict):
        buffer_size = action['size'] if action.get('size') else DEFAULT_BUFFER_SIZE
        data = self.request.recv(buffer_size)
        data = pickle.loads(data)
        return self.action_processor.process(action, data)

    def pre_process_get_action(self, action: dict):
        return self.action_processor.process(action, None)


    def send_success_message(self):
        self.request.send(pickle.dumps({
            "status": StatusCode.SUCCESS.value,
            "message": "SUCCESS"
        }))

    def send_error(self, message: str):
        self.request.send(pickle.dumps({
            "status": 500,
            "message": message
        }))

    def send_data_to_client(self, response):
        response = pickle.dumps(response)
        size = sys.getsizeof(response)
        self.request.send(pickle.dumps({
            "status": StatusCode.SUCCESS.value,
            "size": size
        }))
        logger.info(f"Response: {response}")
        self.request.send(response)


    def send_message(self, message):
        message = pickle.dumps(message)
        self.client.send(message)
        response = self.client.recv(DEFAULT_BUFFER_SIZE)
        if response:
            response = pickle.loads(response)
            if response['status'] == StatusCode.SUCCESS.value:
                return response
            else:
                return response