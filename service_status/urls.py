# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from django.conf.urls import url

from service_status.views import ServiceStatusView

urlpatterns = [
    url(r'^$', ServiceStatusView.as_view(), name='index'),
]
