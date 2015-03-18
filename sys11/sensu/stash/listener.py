# -*- coding: utf-8 -*-
import re
import redis

from sys11.sensu.stash.conf import cfg

pat = re.compile('__keyspace@[^:]+:(.*)')


def listen():
    r = redis.StrictRedis(host=cfg.get('DEFAULT', 'redis_host'),
                          port=cfg.get('DEFAULT', 'redis_port'))

    pubsub = r.pubsub()
    pubsub.psubscribe('__keyspace@*:stash:silence/*')
    for msg in pubsub.listen():
        m = pat.match(msg['channel'])
        if not m:
            continue
        keyname = m.groups(1)
        print("Keyname %s" % keyname)
        if msg['data'] == 'set':
            print("stash set")
        if msg['data'] == 'expire':
            print(msg)
