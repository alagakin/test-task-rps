import pytest

from typing import List, Type
from main import Client
from main import Server
from limiters import SlidingWindowCount, SlidingWindowLog, RequestsLimiter


@pytest.mark.parametrize("limiter, max_capacity, rate, queue_length", [
    (SlidingWindowCount, 5, 0.2, 30),
    (SlidingWindowCount, 20, 0.01, 300),
    (SlidingWindowCount, 100, 1, 300),
    (SlidingWindowLog, 5, 0.2, 30),
    (SlidingWindowLog, 20, 0.01, 300),
    (SlidingWindowLog, 100, 1, 300),

])
def test_rate_does_not_exceed(limiter: Type[RequestsLimiter], max_capacity: int, rate: float, queue_length: int):
    limit_strategy = limiter(max_capacity, rate)
    server = Server(acceptance_rate=90)
    test_queue = [f"{i}" for i in range(queue_length)]
    client = Client(queue=test_queue, server=server, limit_strategy=limit_strategy)

    while True:
        try:
            client.send_next()
        except StopIteration:
            break

    history = server.get_history()
    tolerance_rate = 0.1
    min_difference = find_min_difference(history, max_capacity)
    assert min_difference > (rate - rate * tolerance_rate)


def find_min_difference(history: List[tuple], step: int):
    differences = []
    for i in range(0, len(history), step):
        if i + step < len(history):
            difference = history[i + step][0] - history[i][0]
            differences.append(difference)

    return min(differences)


@pytest.mark.parametrize("queue_length", [1, 100, 1000, 10000])
def test_server_received_all_items(queue_length: int):
    limiter = SlidingWindowCount(10000, 1)
    server = Server(acceptance_rate=80)
    test_queue = [f"{i}" for i in range(queue_length)]
    client = Client(queue=test_queue, server=server, limit_strategy=limiter)

    while True:
        try:
            client.send_next()
        except StopIteration:
            break

    received_items = [item[1] for item in server.get_history()]
    assert test_queue == received_items


@pytest.mark.parametrize("rate", [rate for rate in range(10, 101, 10)])
def test_server_acceptance_rate(rate: int):
    server = Server(acceptance_rate=rate)
    iterations_count = 100_000
    accepted_count = 0
    for i in range(iterations_count):
        if server.receive("test_item"):
            accepted_count += 1

    tolerance = 0.01
    assert abs(accepted_count - rate / 100 * iterations_count) < tolerance * iterations_count
