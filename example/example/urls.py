from django.urls import include, path

urlpatterns = [
    path('', include('service_status.urls', namespace='service-status')),
]
