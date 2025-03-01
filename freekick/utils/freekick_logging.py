import logging
import time
from typing import Any

logging.basicConfig()
_logger = logging.getLogger("FREEKICK")


class Timer:
    def __enter__(self, msg: str="Time Elapsed") -> "Timer":
        self.start = time.perf_counter()
        self.msg=msg
        return self

    def __exit__(self, type: Any, value: Any, traceback: Any) -> None:
        self.time_elapsed = time.perf_counter() - self.start
        _logger.info(f" {self.msg}: {self.time_elapsed:.3f}s")
