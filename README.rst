=====================
Django Service Status
=====================

Django pluggable app to monitor the service status

Documentation
-------------

Django Service Status is a set of checks that are run every time your `http://example.com/service_status/`
page is visited.

Quickstart
----------

Install Django Service Status::

    pip install django-service-status

Add it to your `INSTALLED_APPS`:

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

Features
--------

Builtin checks are:

* database
* swap memory
* celery workers

Default settings: database, swap memory

Add Your Own Checks:
--------------------

You can create a new check like this:

utils/checks.py file:

.. code-block:: python

    from service_status.checks import SystemCheckBase
    from service_status.exceptions import SystemStatusError


    class CustomCheck(SystemCheckBase):
    def __init__(self, **kwargs):
        super(CustomCheck, self).__init__(**kwargs)
        ## Your own initialization logic here
         
    def _run(self):

        ## Your own logic for pass the check.

        if True:
            return 'OK'
        else:
            raise SystemStatusError("An error occured")

Add the CustomCheck in your project setting:

.. code-block:: python

    SERVICE_STATUS_CHECKS  = [
        ('DB_DEFAULT', 'service_status.checks.DatabaseCheck'),
        ('SWAP', 'service_status.checks.SwapCheck'),
        ('CustomCheck', 'utils.checks.CustomCheck')
    ]
    

Running Tests
-------------

Does the code actually work?

::

    source <YOURVIRTUALENV>/bin/activate
    (myenv) $ pip install tox
    (myenv) $ tox

Credits
-------

Tools used in rendering this package:

*  Cookiecutter_
*  `cookiecutter-djangopackage`_

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`cookiecutter-djangopackage`: https://github.com/pydanny/cookiecutter-djangopackage
