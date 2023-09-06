import time
from typing import Union

class Timer:
    def __init__(self) -> None:
        self.start_time = None

    def start(self) -> float:
        self.start_time = time.time()

    def reset(self) -> float:
        self.start_time = None
            
    def get_elapsed_time(self) -> Union[int, float]:
        if self.start_time is None:
            return 0
        return time.time() - self.start_time

    def format_time(self, elapsed_time) -> str:
        minutes, seconds = divmod(int(elapsed_time), 60)
        return f"{minutes}分{seconds}秒"

class CountDownTimer(Timer):
    def __init__(self, duration: Union[int, float]) -> None:
        super().__init__()
        self.duration = duration
    
    def get_remaining_time(self) -> float:
        return self.duration - self.get_elapsed_time()
    
    def is_time_over(self) -> bool:
        return (self.get_remaining_time < 0)
