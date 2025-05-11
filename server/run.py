from threading import Thread
from socketserver import ThreadingTCPServer
from listener import TCPHandler
from logging import getLogger
from utils.base_logging import setup_logging
from constants import SERVER_HOST, SERVER_PORT, NUMBER_OF_THREADS

ThreadingTCPServer.allow_reuse_address = True


setup_logging(file_name="server.log")
logger = getLogger(__name__)

with ThreadingTCPServer((SERVER_HOST, SERVER_PORT), TCPHandler) as server:
    for n in range(NUMBER_OF_THREADS):
        t = Thread(target=server.serve_forever, kwargs={"poll_interval": 1})
        t.daemon = True
        t.start()
    logger.info(f"Started Threads:{NUMBER_OF_THREADS}")

    logger.info(f"Waiting for connections on 127.0.0.1:{9000}...")
    server.serve_forever()
