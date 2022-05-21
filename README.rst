**NOTE!** django-admin-sso uses Google's `oauth2client <https://github.com/googleapis/oauth2client>`__  which has been deprecated for a long time; the repository has even been archived by Google now. django-admin-sso isn't going anywhere but I'd recommend that new projects use `django-authlib's Admin OAuth support <https://github.com/matthiask/django-authlib/#admin-oauth2>`__.

================
Django admin SSO
================

Django admin SSO lets users login to Django's administration panel using an
OAuth2 provider instead of a username/password combination.


Installation
------------

django-admin-sso is most often used with Google OAuth2 and the instructions
follow that assumption. At least in theory it is possible to use a different
OAuth2 provider.

1. Make sure you have a working Django project setup.
2. Install django-admin-sso using pip::

    pip install django-admin-sso

3. Add ``admin_sso`` to ``INSTALLED_APPS`` in your ``settings.py`` file::

    INSTALLED_APPS = (
        ...
        'admin_sso',
        ...
    )

4. Add the django-admin authentication backend::

    AUTHENTICATION_BACKENDS = (
        'admin_sso.auth.DjangoSSOAuthBackend',
        'django.contrib.auth.backends.ModelBackend',
    )

5. Insert your OAuth2 client id and secret key into your settings file::

    DJANGO_ADMIN_SSO_OAUTH_CLIENT_ID = 'your client id here'
    DJANGO_ADMIN_SSO_OAUTH_CLIENT_SECRET = 'your client secret here'

Navigate to Google's
`Developer Console <https://console.developers.google.com/project>`_, create a
new project, and create a new client ID under the menu point "APIs & AUTH",
"Credentials". The redirect URI should be of the form
``http://example.com/admin/admin_sso/assignment/end/``

6. Run ``./manage.py migrate`` to create the needed database tables.

7. Log into the admin and add an Assignment.


Assignments
-----------

Any Remote User -> Local User X
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* Select Username mode "any".
* Set Domain to your authenticating domain.
* Select your local user from the User drop down.


Remote User -> Local User
~~~~~~~~~~~~~~~~~~~~~~~~~
* Select Username mode "matches" *or* "don't match".
* Set username to [not] match by.
* Set Domain to your authenticating domain.
* Select your local user from the User drop down.


Changelog
---------

3.0
~~~

* Dropped support for Django<1.11 and Python<3.
* Modernized the package and reformatted the code using black.


2.4
~~~

* Official support for Django 1.11.

2.3
~~~

* Raised the minimum supported Django version to the LTS version, 1.8.
* Avoid deprecation warnings with Django 1.10.

2.2
~~~

* Official support for Django 1.10 (no changes were necessary)
* Made the admin panel usable on sites with many users.

2.1
~~~

* Removed support for OpenID
* Python 3 compatible
* Dropped support for Django versions older than 1.7
* Continued development as ``django-admin-sso`` (2.0.x versions were released
  independently as ``django-admin-sso2``)

1.0
~~~

* Add support for OAuth2.0 since google closes its OpenID endpoint https://developers.google.com/accounts/docs/OpenID
* Using OpenID is now deprecated and OpenID support will be removed in a future release.
* Add more tests to get a decent coverage.
