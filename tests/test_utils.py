# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import os

import mock
import pytest

from service_status.config import conf
from service_status.utils import get_user_swap


class Test_AppSettings():
    def test__handler(self, settings):
        with pytest.raises(AttributeError) as exception_info:
            assert conf.FOO
        assert str(exception_info.value) == "'Settings' object has no attribute 'SERVICE_STATUS_FOO'"
        settings.SERVICE_STATUS_FOO = 'BAR'
        assert conf.FOO == 'BAR'


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


class Test_get_user_swap():
    def test_no_processes(self, mock_psutil_process_iter):
        assert get_user_swap() == 0
        assert mock_psutil_process_iter.call_count == 1

    def test_processes1(self, mock_psutil_process_iter, mock_process1):
        mock_psutil_process_iter.return_value = [mock_process1]
        assert get_user_swap() == 10
        assert mock_psutil_process_iter.call_count == 1
        assert mock_process1.uids.call_count == 1
        assert mock_process1.memory_full_info.call_count == 1

    def test_processes2(self, mock_psutil_process_iter, mock_process1, mock_process2):
        mock_psutil_process_iter.return_value = [mock_process1, mock_process2]
        assert get_user_swap() == 10
        assert mock_psutil_process_iter.call_count == 1
        assert mock_process1.uids.call_count == 1
        assert mock_process1.memory_full_info.call_count == 1
        assert mock_process2.uids.call_count == 1
        assert mock_process2.memory_full_info.call_count == 1
