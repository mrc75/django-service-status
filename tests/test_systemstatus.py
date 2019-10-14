# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import mock
import pytest

try:
    from django.urls import reverse
except ImportError:
    from django.core.urlresolvers import reverse

from service_status.exceptions import SystemStatusError
from service_status.utils import dummy_celery_app


@pytest.mark.django_db
def test_base(app, mock_time, mock_sentry, mock_get_user_swap):
    url = reverse('service-status:index')
    response = app.get(url)
    assert mock_time.call_count == 4
    assert mock_sentry.call_count == 0
    assert mock_get_user_swap.call_count == 1
    expected = """\
SERVICE_OPERATIONAL
DatabaseCheck DB_DEFAULT: sessions.Session (db: default) 0 OK (7.000s)
SwapCheck SWAP: the user swap memory is: 0 KB (limit: 0 KB) (7.000s)"""
    assert response.pyquery('#main').text() == expected


@pytest.mark.django_db
def test_db_alias(settings_alias, app, mock_time, mock_sentry, mock_get_user_swap):
    url = reverse('service-status:index')
    response = app.get(url)

    assert mock_time.call_count == 6
    assert mock_sentry.call_count == 0
    assert mock_get_user_swap.call_count == 1
    expected = """\
SERVICE_OPERATIONAL
DatabaseCheck DB_DEFAULT: sessions.Session (db: default) 0 OK (7.000s)
DatabaseCheck DB_INTERFACE: auth.group (db: interface) 0 OK (7.000s)
SwapCheck SWAP: the user swap memory is: 0 KB (limit: 0 KB) (7.000s)"""
    assert response.pyquery('#main').text() == expected


@pytest.mark.django_db
def test_celery(settings_celery, app, mock_time):
    url = reverse('service-status:index')
    response = app.get(url)

    assert mock_time.call_count == 2
    expected = """\
SERVICE_OPERATIONAL
CeleryCheck CELERY: got response from 3 worker(s) (7.000s)"""
    assert response.pyquery('#main').text() == expected


@pytest.mark.django_db
def test_celery_notfound(settings_celery, app, mock_time):
    dummy_celery_app.control.response = None
    url = reverse('service-status:index')
    response = app.get(url, status=503)

    assert mock_time.call_count == 2
    expected = """\
ERRORS_FOUND
CeleryCheck CELERY: celery worker `foo` was not found (7.000s)"""
    assert response.pyquery('#main').text() == expected


@pytest.mark.django_db
def test_celery_failure(settings_celery, app, mock_time):
    dummy_celery_app.control.response = 'sbong'
    url = reverse('service-status:index')
    response = app.get(url, status=503)

    assert mock_time.call_count == 2
    expected = """\
ERRORS_FOUND
CeleryCheck CELERY: celery worker `foo` did not respond (7.000s)"""
    assert response.pyquery('#main').text() == expected


@pytest.mark.django_db
def test_warning1(app, mock_dbcheck, mock_time, mock_sentry, mock_get_user_swap):
    url = reverse('service-status:index')
    response = app.get(url)
    assert mock_dbcheck.call_count == 1
    assert mock_time.call_count == 4
    assert mock_sentry.warning.call_count == 1
    assert mock_get_user_swap.call_count == 1
    expected = """\
SERVICE_OPERATIONAL
DatabaseCheck DB_DEFAULT: GOSH (7.000s)
SwapCheck SWAP: the user swap memory is: 0 KB (limit: 0 KB) (7.000s)"""
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
    expected = """\
SERVICE_OPERATIONAL
DatabaseCheck DB_DEFAULT: GOSH (7.000s)
SwapCheck SWAP: the user swap memory is: 4 KB (limit: 0 KB) (7.000s)"""
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
    expected = """\
ERRORS_FOUND
DatabaseCheck DB_DEFAULT: BOOM (7.000s)
SwapCheck SWAP: the user swap memory is: 0 KB (limit: 0 KB) (7.000s)"""
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
    expected = """\
ERRORS_FOUND
DatabaseCheck DB_DEFAULT: WHAT (7.000s)
SwapCheck SWAP: the user swap memory is: 0 KB (limit: 0 KB) (7.000s)"""
    assert response.pyquery('#main').text() == expected


@pytest.mark.django_db
def test_redis_not_connected(settings_redis, app, mock_time):
    url = reverse('service-status:index')
    response = app.get(url, status=503)

    assert mock_time.call_count == 2
    expected = """\
ERRORS_FOUND
RedisCheck REDIS: unable to connect (7.000s)"""
    assert response.pyquery('#main').text() == expected


@mock.patch('service_status.checks.redis')
@pytest.mark.django_db
def test_redis_status_active(redis_mock, settings_redis, app, mock_time):
    url = reverse('service-status:index')
    response = app.get(url, status=200)
    assert redis_mock.StrictRedis.call_count == 1
    expected_args = {'socket_timeout': 0.1, 'host': u'localhost', 'db': u'13', 'port': u'6379'}
    assert redis_mock.StrictRedis.call_args.kwargs == expected_args
    assert mock_time.call_count == 2
    expected = """\
SERVICE_OPERATIONAL
RedisCheck REDIS: active (7.000s)"""
    assert response.pyquery('#main').text() == expected
