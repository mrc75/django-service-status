# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import django_webtest
import pytest
import mock
from django.core.urlresolvers import reverse
from six import PY3

from service_status.exceptions import SystemStatusWarning, SystemStatusError


@pytest.fixture
def app(request):
    wtm = django_webtest.WebTestMixin()
    wtm.csrf_checks = False
    wtm._patch_settings()
    request.addfinalizer(wtm._unpatch_settings)
    return django_webtest.DjangoTestApp()


@pytest.fixture
def time_mock(monkeypatch):
    _mock = mock.Mock()
    _mock.__get__ = mock.Mock(return_value=7)
    monkeypatch.setattr('service_status.checks.SystemCheckBase.elapsed', _mock)
    return _mock


@pytest.fixture
def sentry_mock(monkeypatch):
    _mock = mock.Mock()
    _mock.__get__ = mock.Mock(return_value=7)
    monkeypatch.setattr('service_status.checks.sentry', _mock)
    return _mock


@pytest.fixture
def get_user_swap_mock(monkeypatch):
    _mock = mock.Mock(return_value=0)
    monkeypatch.setattr('service_status.checks.get_user_swap', _mock)
    return _mock


@pytest.mark.xfail(PY3, reason='python3 api changes??? to be investigated...')
@pytest.mark.django_db
def test_base(app, time_mock, sentry_mock, get_user_swap_mock):
    url = reverse('service-status:service-status')
    response = app.get(url)
    assert time_mock.__get__.call_count == 2
    assert sentry_mock.call_count == 0
    assert get_user_swap_mock.call_count == 1
    assert response.pyquery('#main').text() == ('SERVICE_OPERATIONAL '
                                                'DatabaseCheck: OK (7.000s) '
                                                'SwapCheck: the user swap memory is: 0 KB (limit: 0 KB) (7.000s)')


@pytest.mark.xfail(PY3, reason='python3 api changes??? to be investigated...')
@pytest.mark.django_db
def test_warning1(app, time_mock, sentry_mock, get_user_swap_mock):
    url = reverse('service-status:service-status')
    with mock.patch('service_status.checks.DatabaseCheck._run',
                    side_effect=SystemStatusWarning('GOSH')) as _mock1:
        response = app.get(url)
        assert _mock1.call_count == 1
        assert time_mock.__get__.call_count == 2
        assert sentry_mock.warning.call_count == 1
        assert get_user_swap_mock.call_count == 1
        assert response.pyquery('#main').text() == ('WARNINGS_FOUND '
                                                    'DatabaseCheck: GOSH (7.000s) '
                                                    'SwapCheck: the user swap memory is: 0 KB (limit: 0 KB) (7.000s)')


@pytest.mark.xfail(PY3, reason='python3 api changes??? to be investigated...')
@pytest.mark.django_db
def test_warning2(app, time_mock, sentry_mock, get_user_swap_mock):
    url = reverse('service-status:service-status')
    get_user_swap_mock.return_value = 1024
    with mock.patch('service_status.checks.DatabaseCheck._run',
                    side_effect=SystemStatusWarning('GOSH')) as _mock1:
        response = app.get(url)
        assert _mock1.call_count == 1
        assert time_mock.__get__.call_count == 2
        assert sentry_mock.warning.call_count == 2
        assert repr(sentry_mock.warning.call_args_list) == "[call('GOSH'), call(u'the user swap memory is above 0 KB')]"
        assert get_user_swap_mock.call_count == 1
        assert response.pyquery('#main').text() == ('WARNINGS_FOUND '
                                                    'DatabaseCheck: GOSH (7.000s) '
                                                    'SwapCheck: the user swap memory is: 1 KB (limit: 0 KB) (7.000s)')


@pytest.mark.xfail(PY3, reason='python3 api changes??? to be investigated...')
@pytest.mark.django_db
def test_error(app, time_mock, sentry_mock, get_user_swap_mock):
    url = reverse('service-status:service-status')
    with mock.patch('service_status.checks.DatabaseCheck._run',
                    side_effect=SystemStatusError('BOOM')) as _mock:
        response = app.get(url, status=503)
        assert _mock.call_count == 1
        assert time_mock.__get__.call_count == 2
        assert sentry_mock.error.call_count == 1
        assert get_user_swap_mock.call_count == 1
        assert response.pyquery('#main').text() == ('ERRORS_FOUND '
                                                    'DatabaseCheck: BOOM (7.000s) '
                                                    'SwapCheck: the user swap memory is: 0 KB (limit: 0 KB) (7.000s)')


@pytest.mark.xfail(PY3, reason='python3 api changes??? to be investigated...')
@pytest.mark.django_db
def test_exception(app, time_mock, sentry_mock, get_user_swap_mock):
    url = reverse('service-status:service-status')
    with mock.patch('service_status.checks.DatabaseCheck._run',
                    side_effect=Exception('WHAT')) as _mock1:
        response = app.get(url, status=503)
        assert _mock1.call_count == 1
        assert time_mock.__get__.call_count == 2
        assert sentry_mock.exception.call_count == 1
        assert get_user_swap_mock.call_count == 1
        assert response.pyquery('#main').text() == ('ERRORS_FOUND '
                                                    'DatabaseCheck: WHAT (7.000s) '
                                                    'SwapCheck: the user swap memory is: 0 KB (limit: 0 KB) (7.000s)')
