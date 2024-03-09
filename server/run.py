from threading import Thread
from socketserver import ThreadingTCPServer
from server.listener import TCPHandler
from logging import getLogger
from fl_utils.base_logging import setup_logging
ThreadingTCPServer.allow_reuse_address = True


setup_logging(file_name="server.log")
logger = getLogger(__name__)

with ThreadingTCPServer(('0.0.0.0', 9000), TCPHandler) as server:
  for n in range(10):
    t = Thread(target=server.serve_forever, kwargs={'poll_interval': 1})
    t.daemon = True
    t.start()
  logger.info(f"Started Threads:{10}")

  logger.info(f"Waiting for connections on 127.0.0.1:{9000}...")
  server.serve_forever()


