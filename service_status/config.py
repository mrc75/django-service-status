# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from .utils import AppSettings


class ApplicationSettings(AppSettings):
    defaults = {
        'CHECKS': (
            ('DB_DEFAULT', 'service_status.checks.DatabaseCheck'),
            ('SWAP', 'service_status.checks.SwapCheck'),
        ),
        'INIT_DB_DEFAULT': {
            'model_name': 'sessions.Session',
        },
        'INIT_SWAP': {
            'limit': 0,
        },
    }


conf = ApplicationSettings('SERVICE_STATUS')
