# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import functools
import inspect
import os
import six
import time

import psutil
from django.core.exceptions import ImproperlyConfigured
from django.core.signals import setting_changed
from django.utils.module_loading import import_string


class AppSettings(object):
    defaults = {}

    def __init__(self, prefix):
        self.prefix = prefix
        from django.conf import settings

        for name, default in six.iteritems(self.defaults):
            prefix_name = (self.prefix + '_' + name).upper()
            value = getattr(settings, prefix_name, default)
            self._set_attr(prefix_name, value)

        setting_changed.connect(self._handler)

    def _set_attr(self, prefix_name, value):
        name = prefix_name[len(self.prefix) + 1:]
        setter = getattr(self, 'set_%s' % name, None)
        process = getattr(self, 'process_%s' % name, None)
        if process:
            value = process(value)
            setattr(self, name, value)
        elif setter:
            setter(value)
        else:
            setattr(self, name, value)

    def _handler(self, sender, setting, value, **kwargs):
        if setting.startswith(self.prefix):
            self._set_attr(setting, value)

    def _import_by_path(self, attrname, value):
        processed = None
        if isinstance(value, (list, tuple)):
            processed = []
            for entry in value:
                processed.append(import_string(entry))
        elif isinstance(value, six.string_types):
            processed = import_string(value)

        if processed is not None:
            setattr(self, attrname, processed)
        else:
            raise ImproperlyConfigured('Cannot import by path `%s`' % value)


class ContextDecorator(object):
    def __call__(self, f):
        @functools.wraps(f)
        def decorated(*args, **kwds):
            with self:
                return f(*args, **kwds)

        return decorated


class GetTime(ContextDecorator):
    name = None
    t1 = None
    t2 = None
    elapsed = None

    def __init__(self, name=None, doprint=True):
        super(GetTime, self).__init__()
        inspect_stack = inspect.stack()
        self.name = name or inspect_stack[1][3]
        self.doprint = doprint

    def __enter__(self, name=None):
        self.t1 = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.t2 = time.time()
        self.elapsed = self.t2 - self.t1
        message = '{}: {:0.3f}'.format(self.name, self.elapsed)
        if self.doprint:
            print(message)


def get_user_swap():
    total = 0
    for process in psutil.process_iter():
        if process.uids()[0] == os.getuid():
            try:
                total += process.memory_full_info().swap
            except (psutil.AccessDenied, AttributeError):
                pass
    return total
