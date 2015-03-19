import pytest
from sys11.sensu.stash.notifier import MailNotifier, NoopNotifier
from sys11.sensu.stash.listener import get_notifier, listen

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

