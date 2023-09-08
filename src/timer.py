import time
from typing import Union


class Timer:
    def __init__(self) -> None:
        # unit is second
        self.start_time = None
        self.end_time = None
        self.total_seconds = 0

    def start(self) -> float:
        self.start_time = time.time()

    def stop(self) -> float:
        if not self.is_stopped():
            self.end_time = time.time()
            self.total_seconds = self.end_time - self.start_time

    def is_stopped(self) -> bool:
        return self.end_time is not None

    def reset(self) -> float:
        self.start_time = None
        self.end_time = None
        self.total_seconds = 0

    def get_elapsed_time(self) -> Union[int, float]:
        if self.start_time is None:
            return 0
        return time.time() - self.start_time

    def format_time(self, elapsed_time) -> str:
        minutes, seconds = divmod(int(elapsed_time), 60)
        return f"{minutes}分{seconds}秒"


class CountDownTimer(Timer):
    def __init__(self, duration: Union[int, float]) -> None:
        """
        duration : int or float
            Initial duration to count down. The unit is a second.
        """
        super().__init__()
        self.duration = duration
        self.remaining_time_at_stop = None

    def stop(self) -> float:
        self.end_time = time.time()
        self.total_seconds = self.end_time - self.start_time
        self.remaining_time_at_stop = max(0, self.get_remaining_time())

    def get_remaining_time(self) -> float:
        return self.duration - self.get_elapsed_time()

    def is_time_over(self) -> bool:
        return self.get_remaining_time() < 0
