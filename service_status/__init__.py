import django
__version__ = '0.5.0'

if django.VERSION < (3, 2):
    default_app_config = 'service_status.apps.ServiceStatusConfig'
