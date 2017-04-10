from django.conf.urls import url, include

urlpatterns = [
    url(r'^', include('service_status.urls', namespace='service-status')),
]
