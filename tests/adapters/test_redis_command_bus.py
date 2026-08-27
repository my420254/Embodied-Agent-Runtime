from adapters.command_bus import RedisStreamInterruptBus


class FakeRedis:
    def __init__(self):
        self.entries = []
        self.acked = []

    def xgroup_create(self, *args, **kwargs):
        return True

    def xadd(self, stream, fields):
        message_id = f"{len(self.entries) + 1}-0"
        self.entries.append((stream, message_id, dict(fields)))
        return message_id

    def xreadgroup(self, group, consumer, streams, count=1, block=0):
        del group, consumer, streams, block
        if not self.entries:
            return []
        stream, message_id, fields = self.entries.pop(0)
        return [(stream, [(message_id, fields)])][:count]

    def xack(self, stream, group, message_id):
        self.acked.append((stream, group, message_id))
        return 1


def test_redis_stream_bus_normalizes_and_acks_command():
    client = FakeRedis()
    bus = RedisStreamInterruptBus(
        stream="ouragent:test",
        group="runtime",
        consumer="worker-1",
        client=client,
    )

    published = bus.publish("先去拿土豆")
    received = bus.poll()

    assert published["kind"] == "new_task"
    assert received is not None
    assert received["text"] == "先去拿土豆"
    assert received["metadata"]["redis_stream_id"] == "1-0"
    assert bus.ack(received) == 1
    assert client.acked == [("ouragent:test", "runtime", "1-0")]
