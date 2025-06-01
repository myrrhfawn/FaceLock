from logging import getLogger
from socketserver import ThreadingTCPServer
from threading import Thread

from constants import NUMBER_OF_THREADS, SERVER_HOST, SERVER_PORT
from listener import TCPHandler
from utils.base_logging import setup_logging

ThreadingTCPServer.allow_reuse_address = True


setup_logging(file_name="server.log")
logger = getLogger(__name__)

with ThreadingTCPServer((SERVER_HOST, SERVER_PORT), TCPHandler) as server:
    for n in range(NUMBER_OF_THREADS):
        t = Thread(target=server.serve_forever, kwargs={"poll_interval": 1})
        t.daemon = True
        t.start()
    logger.info(f"Started Threads:{NUMBER_OF_THREADS}")

    logger.info(f"Waiting for connections on {SERVER_HOST}:{SERVER_PORT}...")
    server.serve_forever()
