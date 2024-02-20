import sys
from socketserver import StreamRequestHandler, ThreadingMixIn
from io import BytesIO

from logging import getLogger

logger = getLogger(__name__)

class TCPHandler(StreamRequestHandler):
    timeout = 30

    def handle(self):
        try:
            ip_address = self.client_address[0]
            buffer = BytesIO()

            self.data = self.request.recv(8192)

            buffer.write(self.data)
            decoded_message = buffer.getvalue().decode(encoding='utf-8', errors='ignore')
            # Save Message Here
            logger.info(f"Server Recieved Message - {decoded_message}")
            self.request.send("MESSAGE_RECIEVED".encode(encoding='utf-8'))
            self.request.close()

        except ConnectionResetError:
            logger.warning("Connection Reset")
        except Exception:
            logger.exception("Failed to handle request")
        sys.exit(0)