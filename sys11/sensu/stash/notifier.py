# -*- coding: utf-8 -*-
import os
import smtplib
import jinja2
import six
from six.moves import configparser
from six.moves.email_mime_text import MIMEText
from six.moves.email_mime_multipart import MIMEMultipart


class BaseNotifier(object):
    """Just define which functions a notifier should implement"""

    def __init__(self, cfg):
        pass

    def send(self, stash_name, reason):
        """send stash and reason"""
        raise NotImplementedError


class NoopNofifier(BaseNotifier):

    def send(self, stash_name, reason):
        """Does nothing"""
        pass


class MailNotifier(BaseNotifier):

    def __init__(self, cfg):
        self._smpt_host = cfg.get('mailnotifier', 'smtp_host')
        self._smtp_port = cfg.get('mailnotifier', 'smtp_port')
        self._from = cfg.get('mailnotifier', 'from')
        self._to = cfg.get('mailnotifier', 'to')
        module_name = '.'.join(self.__module__.split('.')[:-1])
        try:
            mail_tpl_path = cfg.get('mailnotifier', 'template_path')
            loader = jinja2.FileSystemLoader(mail_tpl_path)
        except configparser.NoOptionError:
            loader = jinja2.PackageLoader(module_name, 'templates')
        try:
            mail_tpl_name = cfg.get('mailnotifier', 'template_name')
        except configparser.NoOptionError:
            mail_tpl_name = 'mailnotifier.txt'
        env = jinja2.Environment(loader=loader)
        self._mail_tpl = env.get_template(mail_tpl_name)

        try:
            self._subject_prefix = cfg.get('mailnotifier', 'subject_prefix')
        except configparser.NoOptionError:
            self._subject_prefix = 'ACK:'

        try:
            uchiwa_url = cfg.get('mailnotifier', 'uchiwa_url')
            self._uchiwa_url = '%s/#/stashes' % uchiwa_url
        except configparser.NoOptionError:
            self._uchiwa_url = 'uchiwa url not configured'

    def _build_msg(self, stash_name, reason):
        msg = MIMEMultipart()
        msg['From'] = self._from
        msg['To'] = self._to
        msg['Subject'] = '%s %s' % (self._subject_prefix, stash_name)
        msg_text = self._mail_tpl.render(stash_name=stash_name,
                                         reason=reason,
                                         uchiwa_url=self._uchiwa_url)
        msg.attach(MIMEText(msg_text, _charset='utf-8'))
        return msg

    def send(self, stash_name, reason):
        if not isinstance(stash_name, six.text_type):
            stash_name = stash_name.decode('utf-8', errors='ignore')
        if not isinstance(reason, six.text_type):
            reason = reason.decode('utf-8', errors='ignore')
        conn = smtplib.SMTP(self._smpt_host, self._smtp_port)
        msg = self._build_msg(stash_name, reason)
        conn.sendmail(self._from, self._to, msg.as_string())
        conn.quit()
