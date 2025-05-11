import time
import threading
import logging

logger = logging.getLogger(__name__)


class FPSCounter(threading.Thread):
    def __init__(self, interval=5.0):
        super().__init__()
        self.interval = interval
        self.frame_count = 0
        self.running = False
        self.lock = threading.Lock()
        self.start()

    def run(self):
        self.running = True
        while self.running:
            start_time = time.time()
            start_count = self._get_and_reset_count()
            time.sleep(self.interval)
            end_count = self._get_and_reset_count()
            elapsed = time.time() - start_time
            fps = (start_count + end_count) / elapsed
            logger.info(f"Pipeline working with {fps:.2f} fps")

    def increment(self):
        with self.lock:
            self.frame_count += 1

    def _get_and_reset_count(self):
        with self.lock:
            count = self.frame_count
            self.frame_count = 0
        return count

    def stop(self):
        self.running = False


# ==== Використання ====

# fps_counter = FPSCounter()
# fps_counter.start()

# while streaming:
#     ... # frame = next frame
#     fps_counter.increment()

# fps_counter.stop()
