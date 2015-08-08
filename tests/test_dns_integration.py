"""Tests for stronglib DNS integration."""

import json
import unittest

import responses
from six.moves.urllib.parse import parse_qs, urlparse

import strongarm
from strongarm.dns_integration import (DnsBlackholeIncrementalUpdater,
                                       DnsBlackholeUpdater,
                                       DnsBlackholeUpdaterException)


class StrongarmDnsTestCase(unittest.TestCase):

    def test_unimplemented(self):
        """Test that running the base classes directly raises NotImplemented."""

        with self.assertRaises(NotImplementedError):
            DnsBlackholeUpdater('127.0.0.1').update_domains(['example.com'])

        with self.assertRaises(NotImplementedError):
            DnsBlackholeIncrementalUpdater('127.0.0.1').update_domains(['example.com'])

    def test_incremental_update(self):
        """
        Test that the incremental updater calculates set differences correctly.

        Do this by implementing a simple incremental updater.

        """

        class SimpleIncrementalUpdater(DnsBlackholeIncrementalUpdater):

            def __init__(self, blackhole_ip, server='localhost'):
                super(SimpleIncrementalUpdater, self).__init__(blackhole_ip, server)

                self.blackholed_domains = []

            def add_domains(self, domains):
                self.blackholed_domains.extend(domains)
                return []

            def remove_domains(self, domains):
                for domain in domains:
                    self.blackholed_domains.remove(domain)
                return []

            def list_domains(self):
                return self.blackholed_domains

        updater = SimpleIncrementalUpdater('127.0.0.1')

        updates = [['example.com', 'example.org'],  # adding two domains
                   ['example.org'],  # removing a domain
                   ['example.com'],  # adding one and removing one
                  ]

        for update in updates:
            updater.update_domains(update)
            self.assertEqual(set(updater.list_domains()), set(update))

    @responses.activate
    def test_lazy_domain_list(self):
        """
        Test that the domain list pages are lazily fetched from the API as the
        domains are being processed.

        Mock a 3-page domain list with 1 domain per page. Implement a simple
        updater that checks the number of requests in `update_domains`.

        """

        pages = 3
        endpoint = strongarm.host + strongarm.Domain.endpoint

        def paginated_domains(request):

            params = parse_qs(urlparse(request.url).query)
            page = int(params['page'][0]) if 'page' in params else 1

            next_url = '%s?page=%d' % (endpoint, page + 1)

            response = {'count': pages,
                        'results': [{'name': '%d.example.com' % page}],
                        'next': next_url if page < pages else None}

            return (200, {}, json.dumps(response))

        responses.add_callback(responses.GET, endpoint,
                               callback=paginated_domains,
                               content_type='application/json')

        class AssertiveUpdater(DnsBlackholeUpdater):

            def __init__(self, blackhole_ip, test_case, server='localhost'):
                super(AssertiveUpdater, self).__init__(blackhole_ip, server)

                self.test_case = test_case

            def update_domains(self, domains):

                # Verify that additional requests are made to the API as the
                # list of domains are being processed.
                for i, domain in enumerate(domains):
                    self.test_case.assertEqual(len(responses.calls), i + 1)

        AssertiveUpdater('127.0.0.1', self).run('some_api_key')
