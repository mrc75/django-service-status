=====
Usage
=====

To use Django Service Status in a project, add it to your `INSTALLED_APPS`:

.. code-block:: python

    INSTALLED_APPS = (
        ...
        'service_status.apps.ServiceStatusConfig',
        ...
    )

Add Django Service Status's URL patterns:

.. code-block:: python

    from service_status import urls as service_status_urls


    urlpatterns = [
        ...
        url(r'^service_status/', include(service_status_urls, namespace='service-status')),
        ...
    ]
