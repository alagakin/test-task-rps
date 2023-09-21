from main import Client


def test_limit_rps(count: int):
    test_queue = [str(i) for i in range(count)]
    client = Client(test_queue)

    for i in range(len(test_queue)):
        client.send(str(i))

    assert client.can_send_request() == False


if __name__ == "__main__":
    test_limit_rps(110)
