stronglib
=========

stronglib is an Apache2 licensed Python library for the
[STRONGARM](http://strongarm.io)
[API](https://strongarm.percipientnetworks.com/api/).

features
--------

- token authentication
- get list of blackholed domains

installation
------------

stronglib is still in beta. The **latest development version** can be
installed directly from GitHub:

.. code-block:: bash

    $ pip install --upgrade https://github.com/percipient/stronglib/tarball/master

usage
-----

Currently the STRONGARM API supports listing all domains.

.. code-block:: python

    import stronglib

    # token authentication
    stronglib.api_key = 'your_api_token'

    # list all blackholed domains
    for domain in stronglib.Domain.all():
        print(domain.name)


documentation
-------------

Documentation is available at ...

contribute
----------

#. Check for open issues or open a fresh issue to start a discussion
   around a feature idea or a bug.
#. If you feel uncomfortable or uncertain about an issue or your changes,
   feel free to email @dicato and he will happily help you.
#. Fork `the repository`_ on GitHub to start making your changes to the
   **master** branch (or branch off of it).
#. Write a test which shows that the bug was fixed or that the feature
   works as expected.
#. Send a pull request and bug the maintainer until it gets merged and
   published. :) Make sure to add yourself to AUTHORS_.

.. _`the repository`: http://github.com/percipient/stronglib
.. _AUTHORS: https://github.com/percipient/strongarm-cli/blob/master/AUTHORS.rst
