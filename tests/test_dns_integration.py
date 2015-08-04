"""Tests for stronglib DNS integration."""

import unittest

from strongarm.dns_integration import (DnsBlackholeIncrementalUpdater,
                                       DnsBlackholeUpdater,
                                       DnsBlackholeUpdaterException)


class StrongarmDnsTestCase(unittest.TestCase):

    def test_unimplemented(self):
        """Test that running the base class directly raises NotImplemented."""

        with self.assertRaises(NotImplementedError):
            DnsBlackholeUpdater('127.0.0.1').update_domains(['example.com'])

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
