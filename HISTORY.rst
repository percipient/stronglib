.. :changelog:

release history
---------------

0.3.0 (2018-08-17)
++++++++++++++++++

* Drop support for Python 3.3, which is end of life.
* Officially support Python 3.6 and 3.7.
* Switch to the next version of the Strongarm API. This allows access to
  blacklisted, whitelisted, and content filtered domains.
    * A new filter() method is added to the Domain resource.
    * The status (blacklisted, whitelisted, or filtered) of a domain is returned.
    * The domain description can be added and viewed.
    * The classification of infections is returned.

0.2.0 (2018-06-29)
++++++++++++++++++

* Fixed an exception when invalid JSON is returned from the Strongarm API. See
  #32. Thanks to @kovacsbalu for reporting and fixing the issue.
* Update the default API host to point to DNSWatch.

0.1.5 (2016-6-22)
+++++++++++++++++

* update default API host

0.1.4 (2016-1-20)
+++++++++++++++++

* add support for Infection endpoint

0.1.3 (2016-1-13)
+++++++++++++++++

* remove duplicate entries when listing domains
* add a `count method` that exposes the number of unique domains

0.1.2 (2015-11-23)
++++++++++++++++++

* update API host to use https://strongarm.io
* update API endpoints to always have a trailing slash

0.1.1 (2015-08-17)
++++++++++++++++++

* update API version header to match http://strongarm.io

0.1.0 (2015-08-12)
++++++++++++++++++

* initial release
