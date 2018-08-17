stronglib
=========

stronglib is an Apache2 licensed Python library for the
`strongarm.io <http://strongarm.io>`_
`API <https://strongarm.percipientnetworks.com/api/>`_.

.. image:: https://travis-ci.org/percipient/stronglib.svg?branch=master
    :target: https://travis-ci.org/percipient/stronglib

.. image:: https://coveralls.io/repos/percipient/stronglib/badge.svg?branch=master
    :target: https://coveralls.io/github/percipient/stronglib

features
--------

- token authentication
- get, create, and delete blackholed domains

installation
------------

The **latest release** can be installed from `PyPI <https://pypi.python.org/pypi/stronglib>`_:

.. code-block:: bash

  $ pip install --upgrade stronglib

The **latest development version** can be installed directly from GitHub:

.. code-block:: bash

    $ pip install --upgrade https://github.com/percipient/stronglib/tarball/master

usage
-----

.. code-block:: python

    import strongarm

    # token authentication
    strongarm.api_key = 'your_api_token'

    # get (ie, search) a single Domain
    domain = strongarm.Domain.get('example.com')
    print(domain.name)

    # list all blackholed domains
    for domain in strongarm.Domain.all():
        print(domain.name)

    # list just blacklisted domains
    for domain in strongarm.Domain.filter(statuses=strongarm.Domain.BLACKLISTED):
        print(domain.name)

    # create a new blackholed domain
    domain = strongarm.Domain.create(name='example.com')

    # create a new whitelisted domain
    domain = strongarm.Domain.create(name='my-company.com',
                                     status=strongarm.Domain.WHITELISTED,
                                     description='Our Company Website')

    # delete a blackholed domain
    domain.delete()

development
-----------

In order to develop stronglib you must install the requirements files.

.. code-block:: bash

    pip install -r requirements.txt

Use pytest to run the test suite:

.. code-block:: bash

    py.test

contribute
----------

#. Check for open issues or open a fresh issue to start a discussion
   around a feature idea or a bug.
#. If you feel uncomfortable or uncertain about an issue or your changes,
   feel free to email support@percipientnetworks.com and we will happily help you.
#. Fork `the repository`_ on GitHub to start making your changes to the
   **master** branch (or branch off of it).
#. Write a test which shows that the bug was fixed or that the feature
   works as expected.
#. Send a pull request and bug the maintainer until it gets merged and
   published. :) Make sure to add yourself to AUTHORS_.

.. _the repository: http://github.com/percipient/stronglib
.. _AUTHORS: https://github.com/percipient/stronglib/blob/master/AUTHORS.rst
