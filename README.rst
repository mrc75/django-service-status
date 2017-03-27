=====================
Django Service Status
=====================

.. image:: https://badge.fury.io/py/django-service-status.svg
    :target: https://badge.fury.io/py/django-service-status

.. image:: https://travis-ci.org/mrc75/django-service-status.svg?branch=master
    :target: https://travis-ci.org/mrc75/django-service-status

.. image:: https://travis-ci.org/mrc75/django-service-status.svg?branch=develop
    :target: https://travis-ci.org/mrc75/django-service-status

.. image:: https://codecov.io/gh/mrc75/django-service-status/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/mrc75/django-service-status

Django pluggable app to monitor the service status

Documentation
-------------

The full documentation is at https://django-service-status.readthedocs.io.

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
        url(r'^', include(service_status_urls)),
        ...
    ]

Features
--------

* TODO

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
