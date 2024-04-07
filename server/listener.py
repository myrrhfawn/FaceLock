import sys
import pickle
from socketserver import StreamRequestHandler, ThreadingMixIn
from server.action_processor import ActionProcessor
from io import BytesIO

from logging import getLogger

logger = getLogger(__name__)

class TCPHandler(StreamRequestHandler):
    def __init__(self, *args, **kwargs):
        self.timeout = 30
        self.action_processor = ActionProcessor()
        super().__init__(*args, **kwargs)

    def handle(self):
        try:
            #ip_address = self.client_address[0]
            buffer = BytesIO()
            logger.info("Request from")
            self.data = self.request.recv(8192)

            buffer.write(self.data)
            #decoded_message = buffer.getvalue().decode(encoding='utf-8', errors='ignore')
            if self.data:
                action = pickle.loads(self.data)
                logger.info(f"action: {action}")
                self.send_success_message()
                if action.get("type"):
                    self.pre_process_action(action)
                    self.send_success_message()
                else:
                    # Save Message Here
                    logger.error(f"Unknown action: {action}")
                    self.send_error("UNKNOWN_ACTION_TYPE")
                self.request.close()
        except ConnectionResetError:
            logger.warning("Connection Reset")
        except Exception:
            logger.exception("Failed to handle request")
        sys.exit(0)

    def pre_process_action(self, action: dict):
        buffer_size = action['size'] if action.get('size') else 8192
        data = self.request.recv(buffer_size)
        data = pickle.loads(data)
        self.action_processor.process(action, data)

    def send_success_message(self):
        self.request.send(pickle.dumps({
            "status": 200,
            "message": "SUCCESS"
        }))

    def send_error(self, message: str):
        self.request.send(pickle.dumps({
            "status": 500,
            "message": message
        }))

