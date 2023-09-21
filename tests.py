import pytest
import asyncio
from main import Client


@pytest.mark.parametrize("max_rps", [1000, 80, 90, 5])
def test_rps_limit(max_rps):
    queue = [str(i) for i in range(100)]
    client = Client(queue, max_rps=max_rps)

    loop = asyncio.get_event_loop()
    start_time = loop.time()

    async def send_and_measure_time():
        await client.send_queue()
        elapsed = loop.time() - start_time
        return elapsed

    elapsed_time = loop.run_until_complete(send_and_measure_time())
    rps = len(queue) / elapsed_time

    tolerance = 1
    assert rps <= max_rps + tolerance
