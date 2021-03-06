from sys11.sensu.stash.conf import cfg

def test_defaults():
    assert cfg.get('DEFAULT', 'redis_host') == 'localhost'
    assert cfg.get('DEFAULT', 'redis_port') == '6379'
    assert cfg.get('DEFAULT', 'notifier') == 'mailnotifier'
    assert cfg.get('DEFAULT', 'logging') == '/etc/sensu/stash_notifier_logging.cfg'

    assert 'mailnotifier' in cfg.sections()

    assert cfg.get('mailnotifier', 'from').startswith('root@')
    assert cfg.get('mailnotifier', 'to').startswith('root@')
    assert cfg.get('mailnotifier', 'smtp_host') == 'localhost'
    assert cfg.get('mailnotifier', 'smtp_port') == '25'
