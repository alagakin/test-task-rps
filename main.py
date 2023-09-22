import random

from collections import deque
from typing import List
from time import time

from limiters import RequestsLimiter


class Server:
    def __init__(self, acceptance_rate: int = 100) -> None:
        self.__history = []
        if acceptance_rate <= 0 or acceptance_rate > 100:
            raise ValueError("Acceptance rate must be between 0 and 100")
        self.__acceptance_rate = acceptance_rate

    def receive(self, item: str) -> bool:
        if self.__can_accept():
            self.__history.append((time(), item))
            return True
        else:
            return False

    def get_history(self) -> List[tuple]:
        return self.__history

    def __can_accept(self) -> bool:
        if random.randint(1, 100) > self.__acceptance_rate:
            return False
        return True


class Client:
    def __init__(self, queue: List[str], server: Server, limit_strategy: RequestsLimiter) -> None:
        self.__queue = deque()
        self.__queue.extend(queue)
        self.__server = server
        self.__strategy = limit_strategy

    def send_next(self) -> bool:
        if len(self.__queue) == 0:
            raise StopIteration('The queue is empty')

        if self.__strategy.can_proceed():
            result = self.__server.receive(self.__queue[0])
            if result:
                self.__queue.popleft()
                return True

        return False
