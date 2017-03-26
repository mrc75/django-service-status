# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import logging
from collections import namedtuple

from django.apps import apps
from django.utils.module_loading import import_string

from service_status.utils import get_user_swap, GetTime
from .config import conf
from .exceptions import SystemStatusError, SystemStatusWarning

sentry = logging.getLogger('sentry')


class SystemCheckBase(object):
    code = None
    output = None
    error = None
    warning = None
    timing = None

    def __init__(self, **kwargs):
        pass

    def __unicode__(self):
        return '{}: {} ({:.3f}s)'.format(self.__class__.__name__, self.output, self.elapsed)

    def _run(self):
        raise NotImplementedError()

    def run(self):
        try:
            with GetTime(doprint=False) as self.timing:
                self.output = self._run() or 'OK'
        except SystemStatusWarning as e:
            self.warning = e
            self.output = str(e)
            log_message = getattr(e, 'log_message', str(e))
            sentry.warning(log_message)
            raise
        except SystemStatusError as e:
            self.error = e
            self.output = str(e)
            log_message = getattr(e, 'log_message', str(e))
            sentry.error(log_message)
            raise
        except Exception as e:
            self.error = SystemStatusError(repr(e))
            self.output = str(e)
            sentry.exception(e)
            raise self.error

    @property
    def status(self):
        if self.error:
            return 'error'

        if self.warning:
            return 'warning'

        return 'normal'

    @property
    def elapsed(self):
        return getattr(self.timing, 'elapsed', None)


class DatabaseCheck(SystemCheckBase):
    code = 'DB'
    model_name = 'sessions.Session'

    def __init__(self, **kwargs):
        super(DatabaseCheck, self).__init__(**kwargs)
        if 'model_name' in kwargs:
            self.model_name = kwargs['model_name']
        self.model = apps.get_model(self.model_name)

    def _run(self):
        self.model.objects.count()


# class SupervisorCheck(SystemCheckBase):
#     """
#     celery                           RUNNING   pid 13835, uptime 0:39:16
#     celery-low-rate                  RUNNING   pid 13838, uptime 0:39:14
#     celery-beat                      RUNNING   pid 13838, uptime 0:39:14
#     nginx                            RUNNING   pid 13836, uptime 0:39:15
#     uwsgi                            RUNNING   pid 13840, uptime 0:39:14
#     """
#
#     def _run(self):
#         command = ['supervisorctl', '-c', '{}/etc/supervisor.ini'.format(os.path.expanduser('~')), 'status']
#         output = subprocess.check_output(command)
#
#         if not output:
#             raise SystemStatusError('`supervisorctl status` command did not respond properly')
#
#         for process in ('celery', 'celery-low-rate', 'celery-beat', 'nginx', 'uwsgi'):
#             if not re.search(r'{}\s+RUNNING'.format(process), output):
#                 raise SystemStatusError('`{}` not found or not running'.format(process))


class SwapCheck(SystemCheckBase):
    code = 'SWAP'
    limit = 0

    def __init__(self, **kwargs):
        super(SwapCheck, self).__init__(**kwargs)
        if 'limit' in kwargs:
            self.limit = kwargs['limit']
        # TODO handle percentage
        # if str(self.limit)[-1] == '%':
        #     self.is_percent = True
        #     self.limit = self.limit[0:-1]
        # self.limit = int(self.limit)

    def _run(self):
        swap = get_user_swap()
        message = 'the user swap memory is: {} KB (limit: {} KB)'.format(swap / 1024, self.limit / 1024)
        if swap > self.limit:
            e = SystemStatusWarning(message)
            e.log_message = 'the user swap memory is above {} KB'.format(self.limit / 1024)
            raise e
        return message


def do_check():
    checks = []
    errors = []
    warnings = []

    for check_name in conf.CHECKS:
        try:
            check_class = import_string(check_name)
            check_init_kwargs = getattr(conf, 'INIT_{}'.format(check_class.code), {})
            check = check_class(**check_init_kwargs)
            checks.append(check)
            check.run()
        except SystemStatusError as e:
            errors.append(e)
        except SystemStatusWarning as e:
            warnings.append(e)

    return namedtuple('SystemErrors', ('checks', 'errors', 'warnings'))(checks, errors, warnings)
