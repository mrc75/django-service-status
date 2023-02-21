# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from django.urls import path

from service_status.views import ServiceStatusView

app_name = 'service-status'

urlpatterns = [
    path('', ServiceStatusView.as_view(), name='index'),
]
