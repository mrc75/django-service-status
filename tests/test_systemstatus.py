# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import django_webtest
import itertools
import pytest
import mock
from django.core.urlresolvers import reverse

from service_status.exceptions import SystemStatusWarning, SystemStatusError
from service_status.utils import dummy_celery_app


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


@pytest.yield_fixture()
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


@pytest.yield_fixture()
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


@pytest.mark.django_db
def test_base(app, mock_time, mock_sentry, mock_get_user_swap):
    url = reverse('service-status:index')
    response = app.get(url)
    assert mock_time.call_count == 4
    assert mock_sentry.call_count == 0
    assert mock_get_user_swap.call_count == 1
    expected = ('SERVICE_OPERATIONAL '
                'DatabaseCheck DB_DEFAULT: sessions.Session (db: default) 0 OK (7.000s) '
                'SwapCheck SWAP: the user swap memory is: 0 KB (limit: 0 KB) (7.000s)')
    assert response.pyquery('#main').text() == expected


@pytest.mark.django_db
def test_db_alias(settings_alias, app, mock_time, mock_sentry, mock_get_user_swap):
    url = reverse('service-status:index')
    response = app.get(url)

    assert mock_time.call_count == 6
    assert mock_sentry.call_count == 0
    assert mock_get_user_swap.call_count == 1
    expected = ('SERVICE_OPERATIONAL '
                'DatabaseCheck DB_DEFAULT: sessions.Session (db: default) 0 OK (7.000s) '
                'DatabaseCheck DB_INTERFACE: auth.group (db: interface) 0 OK (7.000s) '
                'SwapCheck SWAP: the user swap memory is: 0 KB (limit: 0 KB) (7.000s)')
    assert response.pyquery('#main').text() == expected


@pytest.mark.django_db
def test_celery(settings_celery, app, mock_time):
    url = reverse('service-status:index')
    response = app.get(url)

    assert mock_time.call_count == 2
    expected = ('SERVICE_OPERATIONAL '
                'CeleryCheck CELERY: got response from 3 worker(s) (7.000s)')
    assert response.pyquery('#main').text() == expected


@pytest.mark.django_db
def test_celery_notfound(settings_celery, app, mock_time):
    dummy_celery_app.control.response = None
    url = reverse('service-status:index')
    response = app.get(url, status=503)

    assert mock_time.call_count == 2
    expected = ('ERRORS_FOUND '
                'CeleryCheck CELERY: celery worker `foo` was not found (7.000s)')
    assert response.pyquery('#main').text() == expected


@pytest.mark.django_db
def test_celery_failure(settings_celery, app, mock_time):
    dummy_celery_app.control.response = 'sbong'
    url = reverse('service-status:index')
    response = app.get(url, status=503)

    assert mock_time.call_count == 2
    expected = ('ERRORS_FOUND '
                'CeleryCheck CELERY: celery worker `foo` did not respond (7.000s)')
    assert response.pyquery('#main').text() == expected


@pytest.mark.django_db
def test_warning1(app, mock_dbcheck, mock_time, mock_sentry, mock_get_user_swap):
    url = reverse('service-status:index')
    response = app.get(url)
    assert mock_dbcheck.call_count == 1
    assert mock_time.call_count == 4
    assert mock_sentry.warning.call_count == 1
    assert mock_get_user_swap.call_count == 1
    expected = ('WARNINGS_FOUND '
                'DatabaseCheck DB_DEFAULT: GOSH (7.000s) '
                'SwapCheck SWAP: the user swap memory is: 0 KB (limit: 0 KB) (7.000s)')
    assert response.pyquery('#main').text() == expected


@pytest.mark.django_db
def test_warning2(app, mock_dbcheck, mock_time, mock_sentry, mock_get_user_swap):
    mock_get_user_swap.return_value = 4 * 1024
    url = reverse('service-status:index')
    response = app.get(url)
    assert mock_dbcheck.call_count == 1
    assert mock_time.call_count == 4
    assert mock_sentry.warning.call_count == 2
    assert mock_sentry.warning.call_args_list == [mock.call('GOSH'),
                                                  mock.call(u'the user swap memory is above 0 KB')]
    assert mock_get_user_swap.call_count == 1
    expected = ('WARNINGS_FOUND '
                'DatabaseCheck DB_DEFAULT: GOSH (7.000s) '
                'SwapCheck SWAP: the user swap memory is: 4 KB (limit: 0 KB) (7.000s)')
    assert response.pyquery('#main').text() == expected


@pytest.mark.django_db
def test_error(app, mock_dbcheck, mock_time, mock_sentry, mock_get_user_swap):
    mock_dbcheck.side_effect = SystemStatusError('BOOM')
    url = reverse('service-status:index')
    response = app.get(url, status=503)
    assert mock_dbcheck.call_count == 1
    assert mock_time.call_count == 4
    assert mock_sentry.error.call_count == 1
    assert mock_get_user_swap.call_count == 1
    expected = ('ERRORS_FOUND '
                'DatabaseCheck DB_DEFAULT: BOOM (7.000s) '
                'SwapCheck SWAP: the user swap memory is: 0 KB (limit: 0 KB) (7.000s)')
    assert response.pyquery('#main').text() == expected


@pytest.mark.django_db
def test_exception(app, mock_dbcheck, mock_time, mock_sentry, mock_get_user_swap):
    mock_dbcheck.side_effect = Exception('WHAT')
    url = reverse('service-status:index')
    response = app.get(url, status=503)
    assert mock_dbcheck.call_count == 1
    assert mock_time.call_count == 4
    assert mock_sentry.exception.call_count == 1
    assert mock_get_user_swap.call_count == 1
    expected = ('ERRORS_FOUND '
                'DatabaseCheck DB_DEFAULT: WHAT (7.000s) '
                'SwapCheck SWAP: the user swap memory is: 0 KB (limit: 0 KB) (7.000s)')
    assert response.pyquery('#main').text() == expected
