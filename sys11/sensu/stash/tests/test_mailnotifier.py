import pytest
from sys11.sensu.stash.notifier import MailNotifier

@pytest.fixture
def conf():
    from six.moves import configparser
    cfg = configparser.ConfigParser()
    cfg.add_section('mailnotifier')
    cfg.set('mailnotifier', 'smtp_host', 'localhost')
    cfg.set('mailnotifier', 'smtp_port', '25')
    cfg.set('mailnotifier', 'from', 'root@localhost')
    cfg.set('mailnotifier', 'to', 'root@localhost')
    return cfg

def test_build_msg(conf):
    from six.moves.email_mime_multipart import MIMEMultipart
    notifier = MailNotifier(conf)
    assert isinstance(notifier._build_msg('A', 'B'), MIMEMultipart)
