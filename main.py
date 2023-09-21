import time
from typing import List


class Client:
    __queue: List[str]
    __queries_count: int = 0
    __rps: int = 0
    MAX_RPS = 100

    def __init__(self, queue: list):
        self.__queue = queue

    def send(self, item: str):
        self.__queries_count += 1

    def send_queue(self):
        start = time.perf_counter()
        for item in self.__queue:
            if self.can_send_request(start):
                self.send(item)

    def can_send_request(self, start):
        now = time.perf_counter()
        if self.__queries_count / (now - start) > self.MAX_RPS:
            time.sleep(1)
            return self.can_send_request(start)
        else:
            return True


if __name__ == "__main__":
    client = Client([str(i) for i in range(200)])
    client.send_queue()
