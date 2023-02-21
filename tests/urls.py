# -*- coding: utf-8
from __future__ import unicode_literals, absolute_import

from django.urls import include, path

urlpatterns = [
    path('', include('service_status.urls', namespace='service-status')),
]
