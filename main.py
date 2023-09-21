import asyncio
import time
from typing import List


class Client:
    def __init__(self, queue: List[str], max_rps: int = 100):
        self.__queue = queue
        self.__max_rps = max_rps
        self.__queries_count = 0
        self.__last_request_time = 0

    async def send(self, item: str) -> bool:
        self.__queries_count += 1
        # in case of success request:
        return True

    async def send_queue(self):
        for item in self.__queue:
            if await self.send(item):
                await self.limit_rps()

    async def limit_rps(self):
        current_time = time.perf_counter()
        time_elapsed = current_time - self.__last_request_time
        if time_elapsed < 1 / self.__max_rps:
            await asyncio.sleep(1 / self.__max_rps - time_elapsed)
        self.__last_request_time = time.perf_counter()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    client = Client([f'{i}' for i in range(200)], max_rps=100)
    try:
        loop.run_until_complete(client.send_queue())
    finally:
        print('close')
