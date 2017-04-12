# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import inspect
import os
import six
from time import time

import psutil
from django.core.signals import setting_changed


class AppSettings(object):
    defaults = {}

    def __init__(self, prefix):
        self.prefix = prefix
        from django.conf import settings

        self.django_settings = settings

        for name, default in six.iteritems(self.defaults):
            prefix_name = (self.prefix + '_' + name).upper()
            value = getattr(self.django_settings, prefix_name, default)
            self._set_attr(prefix_name, value)

        setting_changed.connect(self._handler)

    def _set_attr(self, prefix_name, value):
        name = prefix_name[len(self.prefix) + 1:]
        setattr(self, name, value)

    def _handler(self, sender, setting, value, **kwargs):
        if kwargs['enter'] and setting.startswith(self.prefix):
            self._set_attr(setting, value)

    def __getattr__(self, name):
        return getattr(self.django_settings, '_'.join([self.prefix, name]))


class GetTime(object):
    name = None
    t1 = None
    t2 = None
    elapsed = None

    def __init__(self, name=None, doprint=False):
        super(GetTime, self).__init__()
        inspect_stack = inspect.stack()
        self.name = name or inspect_stack[1][3]
        self.doprint = doprint

    def __enter__(self, name=None):
        self.t1 = time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.t2 = time()
        self.elapsed = self.t2 - self.t1
        message = '{}: {:0.3f}'.format(self.name, self.elapsed)
        if self.doprint:  # pragma: no cover
            print(message)


def get_user_swap():
    total = 0
    for process in psutil.process_iter():
        if process.uids()[0] == os.getuid():
            try:
                total += process.memory_full_info().swap
            except (psutil.AccessDenied, psutil.NoSuchProcess, AttributeError):
                pass
    return total


class DummyCeleryApp(object):
    def __init__(self):
        class Control(object):
            response = 'pong'

            def ping(self, names):
                if not self.response:
                    return None
                return [{name: {'ok': self.response}} for name in names]

        self.control = Control()


dummy_celery_app = DummyCeleryApp()
