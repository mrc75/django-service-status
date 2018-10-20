# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import itertools
import os

import django_webtest
import mock
import pytest

from service_status.exceptions import SystemStatusWarning


@pytest.fixture
def app(request):
    wtm = django_webtest.WebTestMixin()
    wtm.csrf_checks = False
    wtm._patch_settings()
    request.addfinalizer(wtm._unpatch_settings)
    return django_webtest.DjangoTestApp()


@pytest.fixture
def mock_dbcheck(monkeypatch):
    _mock = mock.Mock(side_effect=SystemStatusWarning('GOSH'))
    monkeypatch.setattr('service_status.checks.DatabaseCheck._run', _mock)
    return _mock


@pytest.fixture
def mock_time(monkeypatch):
    _mock = mock.Mock(side_effect=itertools.cycle([3, 10]))
    monkeypatch.setattr('service_status.utils.time', _mock)
    return _mock


@pytest.fixture
def mock_sentry(monkeypatch):
    _mock = mock.Mock()
    _mock.__get__ = mock.Mock(return_value=7)
    monkeypatch.setattr('service_status.checks.sentry', _mock)
    return _mock


@pytest.fixture
def mock_get_user_swap(monkeypatch):
    _mock = mock.Mock(return_value=0)
    monkeypatch.setattr('service_status.checks.get_user_swap', _mock)
    return _mock


@pytest.fixture()
def settings_alias(settings):
    from service_status.config import conf

    settings.SERVICE_STATUS_CHECKS = (
        ('DB_DEFAULT', 'service_status.checks.DatabaseCheck'),
        ('DB_INTERFACE', 'service_status.checks.DatabaseCheck'),
        ('SWAP', 'service_status.checks.SwapCheck'),
    )

    settings.SERVICE_STATUS_INIT_DB_INTERFACE = {
        'model_name': 'auth.group',
        'database_alias': 'interface',
    }
    yield
    delattr(settings, 'SERVICE_STATUS_CHECKS')
    delattr(settings, 'SERVICE_STATUS_INIT_DB_INTERFACE')
    conf.__init__(conf.prefix)


@pytest.fixture()
def settings_celery(settings):
    from service_status.config import conf

    settings.SERVICE_STATUS_CHECKS = (
        ('CELERY', 'service_status.checks.CeleryCheck'),
    )
    settings.SERVICE_STATUS_INIT_CELERY = {
        'celery_app_fqn': 'service_status.utils.dummy_celery_app',
        'worker_names': ['foo', 'bar', 'baz'],
    }
    yield
    delattr(settings, 'SERVICE_STATUS_CHECKS')
    delattr(settings, 'SERVICE_STATUS_INIT_CELERY')
    conf.__init__(conf.prefix)


@pytest.fixture
def mock_psutil_process_iter(monkeypatch):
    _mock = mock.Mock(return_value=[])
    monkeypatch.setattr('psutil.process_iter', _mock)
    return _mock


@pytest.fixture
def mock_process1(monkeypatch):
    _mock = mock.Mock()
    # process.uids()[0] == os.getuid():
    _mock.uids.return_value = [os.getuid()]
    # process.memory_full_info().swap
    _mock.memory_full_info.return_value.swap = 10
    return _mock


@pytest.fixture
def mock_process2(monkeypatch):
    _mock = mock.Mock()
    # process.uids()[0] == os.getuid():
    _mock.uids.return_value = [os.getuid()]
    # process.memory_full_info().swap
    _mock.memory_full_info.side_effect = AttributeError('opss')
    return _mock
