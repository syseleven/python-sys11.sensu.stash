# -*- coding: utf-8 -*-
from __future__ import print_function
import os
import time
import re
import redis
import json
import logging
import logging.config
import argparse
import pkg_resources

from sys11.sensu.stash.conf import cfg

pat = re.compile('__keyspace@[^:]+:(.*)')
default_config_file = '/etc/sensu/stash_notifier.cfg'
log = logging.getLogger('sys11.sensu.stash')


def get_notifier(name):
    for ep in pkg_resources.iter_entry_points('sys11.sensu.stash.notifiers',
        name=name):
        return ep.load()
    return None

def listen(redis_conn, notifier):
    pubsub = redis_conn.pubsub()
    pubsub.psubscribe('__keyspace@*:stash:silence/*')
    for msg in pubsub.listen():
        m = pat.match(msg['channel'])
        if not m:
            continue
        keyname = m.group(1)
        if msg['data'] == 'set':
            val = redis_conn.get(keyname)
            reason = 'Without any reason.'
            if val:
                try:
                    data = json.loads(val)
                    if data['reason']:
                        reason = data['reason']
                except KeyError:
                    pass
                except ValueError:
                    pass
            log.info('Sending infos about %s via %s', keyname, repr(notifier))
            notifier.send(keyname, reason)

def setup_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', dest='config_file',
        default=default_config_file,
        help='Config file to override defaults.')
    return parser

def connect_to_redis(conf):
    redis_conn = None
    while redis_conn is None:
        redis_conn = redis.StrictRedis(host=conf.get('DEFAULT', 'redis_host'),
                                       port=int(conf.get('DEFAULT', 'redis_port')))
        try:
            redis_conn.ping()
            log.info('Connection to redis %s:%s established', conf.get('DEFAULT', 'redis_host'),
                    conf.get('DEFAULT', 'redis_port'))
        except redis.exceptions.RedisError:
            log.error('Unable to connect to redis %s:%s. Trying again in 10 seconds',
                    conf.get('DEFAULT', 'redis_host'), conf.get('DEFAULT', 'redis_port'))
            time.sleep(10)
            redis_conn = None
    return redis_conn

def main():
    try:
        opts = setup_args().parse_args()
        if not os.path.isfile(opts.config_file):
            if opts.config_file != default_config_file:
                print("No such file: ", opts.config_file)
                exit(1)
        else:
            cfg.readfp(open(opts.config_file, 'r'))
        notifier = get_notifier(cfg.get('DEFAULT', 'notifier'))
        if not notifier:
            print("Unable to find requested notifier", cfg.get('DEFAULT', 'notifier'))
            exit(1)
        if os.path.isfile(cfg.get('DEFAULT', 'logging')):
            logging.config.fileConfig(cfg.get('DEFAULT', 'logging'))
        else:
            logging.basicConfig()
        log.setLevel(logging.INFO)
        redis_conn = connect_to_redis(cfg)

        listen(redis_conn, notifier(cfg))
    except KeyboardInterrupt:
        exit(0)
