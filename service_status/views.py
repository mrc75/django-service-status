# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.generic.base import TemplateView

from .checks import do_check


class ServiceStatusView(TemplateView):
    template_name = 'service_status/service_status.html'
    response_status_code = 200

    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        return super(ServiceStatusView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        status = do_check()

        if status.errors:
            self.response_status_code = 503
            response_tag = 'ERRORS_FOUND'
        # elif status.warnings:
        #     response_tag = 'WARNINGS_FOUND'
        else:
            response_tag = 'SERVICE_OPERATIONAL'

        kwargs.update({
            'status': status,
            'response_tag': response_tag
        })
        return super(ServiceStatusView, self).get_context_data(**kwargs)

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context, status=self.response_status_code)
