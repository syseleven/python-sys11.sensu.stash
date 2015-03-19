# -*- coding: utf-8 -*-
import socket
from six.moves import configparser

config_defaults = {
        'redis_host': 'localhost',
        'redis_port': '6379',
        'notifier': 'mailnotifier',
        'logging': '/etc/sensu/stash_notifier_logging.cfg',
        }

cfg = configparser.ConfigParser(defaults=config_defaults)
cfg.add_section('mailnotifier')
cfg.set('mailnotifier', 'from', 'root@%s' % socket.getfqdn())
cfg.set('mailnotifier', 'to', 'root@%s' % socket.getfqdn())
cfg.set('mailnotifier', 'smtp_host', 'localhost')
cfg.set('mailnotifier', 'smtp_port', '25')
