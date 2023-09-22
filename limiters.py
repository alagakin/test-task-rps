from time import time, sleep
from abc import ABC, abstractmethod


class RequestsLimiter(ABC):
    _max_capacity: int
    _unit: float

    def __init__(self, max_capacity: int, unit_in_seconds: float = 1.0) -> None:
        self._max_capacity = max_capacity
        self._unit = unit_in_seconds

    @abstractmethod
    def can_proceed(self) -> bool:
        pass


class SlidingWindowCount(RequestsLimiter):

    def __init__(self, max_capacity: int, unit_in_seconds: float = 1.0) -> None:
        super().__init__(max_capacity, unit_in_seconds)

        self.__current_time = time()
        self.__prev_count = max_capacity
        self.__current_count = 0

    def can_proceed(self) -> bool:
        if (time() - self.__current_time) > self._unit:
            self.__current_time = time()
            self.__prev_count = self.__current_count
            self.__current_count = 0

        sliding_capacity = (self.__prev_count * (
                self._unit - (time() - self.__current_time)) / self._unit) + self.__current_count

        if sliding_capacity > self._max_capacity:
            return False

        self.__current_count += 1
        return True


class SlidingWindowLog(RequestsLimiter):
    def __init__(self, max_capacity: int, unit_in_seconds: float = 1.0) -> None:
        super().__init__(max_capacity, unit_in_seconds)
        self.__log = []

    def can_proceed(self) -> bool:
        current_time = time()
        self.__log.append(current_time)
        self.__cleanup_log(current_time)
        if len(self.__log) <= self._max_capacity:
            return True
        else:
            self.__cool_down()
            return False

    def __cleanup_log(self, current_time) -> None:
        cutoff_time = current_time - self._unit
        self.__log = [tm for tm in self.__log if tm >= cutoff_time]

    def __cool_down(self):
        sleep(self._unit)
