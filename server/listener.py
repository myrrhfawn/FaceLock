import sys
import pickle
import time
from socketserver import StreamRequestHandler


from action_processor import ActionProcessor
from io import BytesIO
from constants import DEFAULT_BUFFER_SIZE, HANDLER_TIMEOUT, StatusCode
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
            # decoded_message = buffer.getvalue().decode(encoding='utf-8', errors='ignore')
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
                    response = self.pre_process_post_action(action)
                    if response:
                        self.send_data_to_client(response)
                    else:
                        self.send_success_message()
        except ConnectionResetError:
            logger.warning("Connection Reset")
        except Exception as e:
            logger.exception(f"Failed to handle request: {e}")
        finally:
            self.request.close()
        # sys.exit(0)

    def pre_process_post_action(self, action: dict):
        buffer_size = action["size"] if action.get("size") else DEFAULT_BUFFER_SIZE
        data = self.request.recv(buffer_size)
        data = pickle.loads(data)
        return self.action_processor.process(action, data)

    def pre_process_get_action(self, action: dict):
        data = None
        logger.info(f"Processing GET action: {action}")
        if action.get("size", DEFAULT_BUFFER_SIZE) > 38:
            self.send_success_message()
            logger.info("Receiving data from client")
            buffer_size = action["size"] if action.get("size") else DEFAULT_BUFFER_SIZE
            data = self.request.recv(buffer_size)
            data = pickle.loads(data)
        return self.action_processor.process(action, data)

    def send_success_message(self):
        self.request.send(
            pickle.dumps({"status": StatusCode.SUCCESS.value, "message": "SUCCESS"})
        )

    def send_error(self, message: str):
        self.request.send(pickle.dumps({"status": 500, "message": message}))

    def send_data_to_client(self, response: dict = None):
        response = pickle.dumps(response)
        size = sys.getsizeof(response)
        logger.info(f"Sending response of size: {size} bytes")
        self.request.send(
            pickle.dumps({"status": StatusCode.SUCCESS.value, "size": size})
        )
        time.sleep(0.1)  # Simulate some processing delay, if remove send data will be merged into one packet
        if response:
            self.request.send(response)
