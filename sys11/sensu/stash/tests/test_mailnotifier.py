import pytest
import jinja2
from sys11.sensu.stash.notifier import MailNotifier
import six

@pytest.fixture
def conf():
    from six.moves import configparser
    cfg = configparser.ConfigParser()
    cfg.add_section('mailnotifier')
    cfg.set('mailnotifier', 'smtp_host', 'localhost')
    cfg.set('mailnotifier', 'smtp_port', '587')
    cfg.set('mailnotifier', 'from', 'root@here')
    cfg.set('mailnotifier', 'to', 'root@there')
    return cfg

@pytest.fixture
def init_conf():
    cfg = conf()

    cfg.set('mailnotifier', 'subject_prefix', 'HELLO')
    cfg.set('mailnotifier', 'uchiwa_url', 'http://localhost:3001')
    cfg.set('mailnotifier', 'template_name', 'testing.txt')

    return cfg


def test_init(conf):
    notifier = MailNotifier(conf)

    assert notifier._smtp_host == 'localhost'
    assert notifier._smtp_port == '587'
    assert notifier._from == 'root@here'
    assert notifier._to == 'root@there'
    assert notifier._subject_prefix == 'ACK:'
    assert notifier._uchiwa_url == 'uchiwa url not configured'
    assert isinstance(notifier._mail_tpl, jinja2.environment.Template)
    assert notifier._mail_tpl.filename.endswith('sys11/sensu/stash/templates/mailnotifier.txt')


def test_init_optional_stuff(init_conf, tmpdir):
    tmpd = tmpdir.mkdir('funny_templates')
    tmpf = tmpd.join('testing.txt')
    tmpf.write('Hello World')
    init_conf.set('mailnotifier', 'template_path', tmpd.strpath)
    notifier = MailNotifier(init_conf)

    assert notifier._smtp_host == 'localhost'
    assert notifier._smtp_port == '587'
    assert notifier._from == 'root@here'
    assert notifier._to == 'root@there'
    assert notifier._subject_prefix == 'HELLO'
    assert notifier._uchiwa_url == 'http://localhost:3001/#/stashes'
    assert isinstance(notifier._mail_tpl, jinja2.environment.Template)
    assert notifier._mail_tpl.filename.endswith('/funny_templates/testing.txt')


def test_build_msg(conf):
    from six.moves.email_mime_multipart import MIMEMultipart
    notifier = MailNotifier(conf)
    msg = notifier._build_msg('A', 'B')
    assert isinstance(msg, MIMEMultipart)

    assert msg['From'] == 'root@here'
    assert msg['To'] == 'root@there'
    assert msg['Subject'] == 'ACK: A'
    assert len(msg._payload) == 1
    assert msg._payload[0].get_charset() == 'utf-8'

def test_convert_for_mail():
    res = MailNotifier._convert_for_mail('test')
    assert isinstance(res, six.text_type)

def test_send(conf, monkeypatch):
    from six.moves.email_mime_multipart import MIMEMultipart
    def fake_connect(*args, **kwargs):
        return 220, 'ping'

    def fake_sendmail(self, from_addr, to_addrs, msg, mail_options=[],
            rcpt_options=[]):
        assert from_addr == 'root@here'
        assert to_addrs == 'root@there'
        assert 'Subject: ACK: ' in msg

    monkeypatch.setattr('smtplib.SMTP.connect', fake_connect)
    monkeypatch.setattr('smtplib.SMTP.sendmail', fake_sendmail)
    monkeypatch.setattr('smtplib.SMTP.quit', lambda x: None)
    notifier = MailNotifier(conf)
    notifier.send('stashname', 'just for fun')
