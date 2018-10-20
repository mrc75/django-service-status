# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

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
