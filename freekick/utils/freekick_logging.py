import logging
import time

logging.basicConfig()
_logger = logging.getLogger("FREEKICK")


class Timer:
    def __enter__(self):
        self.start = time.perf_counter()
        return self

    def __exit__(self, type, value, traceback):
        self.time_elapsed = time.perf_counter() - self.start
        _logger.info(f"Time Elapsed: {self.time_elapsed:.3f}s")
