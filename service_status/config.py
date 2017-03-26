# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from .utils import AppSettings


class ApplicationSettings(AppSettings):
    defaults = {
        'CHECKS': (
            'service_status.checks.DatabaseCheck',
            'service_status.checks.SwapCheck',
        ),
        'INIT_DB': {
            'model_name': 'sessions.Session',
        },
        'INIT_SWAP': {
            'limit': 0,
        },
    }


conf = ApplicationSettings('SERVICE_STATUS')
