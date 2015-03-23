import pytest
import redis
from six.moves.configparser import ConfigParser
from sys11.sensu.stash.notifier import MailNotifier, NoopNotifier
from sys11.sensu.stash.listener import get_notifier, listen, connect_to_redis

def test_get_notifier():
    cls = get_notifier('mailnotifier')
    assert cls == MailNotifier

def test_get_notifier_noop():
    cls = get_notifier('noopnotifier')
    assert cls == NoopNotifier

def test_get_notifier_not_found():
    cls = get_notifier('DEFINITELY_NOT_EXISTING')
    assert cls == None

class PubSubFake(object):
    def listen(self):
        yield {'pattern': '__keyspace@*:stash:silence/*',
               'type': 'pmessage',
               'channel': '__keyspace@0__:stash:silence/puppetmaster.local',
               'data': 'set'}
        yield {'pattern': '__keyspace@*:stash:silence/*',
               'type': 'pmessage',
               'channel': '__keyspace@0__:stash:silence/puppetmaster.local',
               'data': 'set'}
        yield {'pattern': '__keyspace@*:stash:silence/*',
               'type': 'pmessage',
               'channel': '__keyspace@0__:stash:silence/puppetmaster.local',
               'data': 'expire'}

    def psubscribe(self, name):
        assert name == '__keyspace@*:stash:silence/*'

class RedisFake(object):
    def __init__(self):
        self._get_cnt = 0

    def get(self, keyname):
        if self._get_cnt == 0:
            res = '{"reason": "testing"}'
        elif self._get_cnt == 1:
            res = '{"reason": ""}'

        self._get_cnt += 1
        return res

    def pubsub(self):
        return PubSubFake()

class TestNotifier(object):
    def __init__(self):
        self._send_cnt = 0

    def send(self, keyname, reason):
        if self._send_cnt == 0:
            assert reason == 'testing'
        elif self._send_cnt == 1:
            assert reason == 'Without any reason.'

        self._send_cnt += 1
        

def test_listen():
    redis_conn = RedisFake()
    notifier = TestNotifier()
    listen(redis_conn, notifier)

    assert redis_conn._get_cnt == 2
    assert notifier._send_cnt == 2

class AnotherFakeRedis:
    def __init__(self, *args, **kwargs):
        self._call_cnt = 0

    def __call__(self, *args, **kwargs):
        self._call_cnt += 1
        if self._call_cnt == 1:
            raise redis.exceptions.ConnectionError('does not work')
        elif self._call_cnt == 2:
            raise redis.exceptions.RedisError('does not work')
        else:
            return 'works'

class FakeSleep:
    def __init__(self):
        self._call_cnt = 0

    def __call__(self, *args):
        self._call_cnt += 1

def test_connect_to_redis(monkeypatch):
    fake_redis = AnotherFakeRedis()
    fake_sleep = FakeSleep()
    cfg = ConfigParser(defaults={'redis_host': 'localhost',
                                 'redis_port': '1234'})
    monkeypatch.setattr('redis.StrictRedis.ping', fake_redis)
    monkeypatch.setattr('time.sleep', fake_sleep)

    res = connect_to_redis(cfg)
    assert isinstance(res, redis.StrictRedis)
    assert fake_redis._call_cnt == 3
    assert fake_sleep._call_cnt == 2
