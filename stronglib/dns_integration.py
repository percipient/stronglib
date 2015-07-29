from stronglib.core import Stronglib, StronglibException


class DnsBlackholeUpdaterException(Exception):
    """
    An error occurred in the DNS blackhole updater.

    """


class DnsBlackholeUpdater(object):
    """
    Abstract base class for a DNS server integration that updates the list of
    blackholed domains.

    Each DNS server integration should subclass and implement `update_domains`.

    Call `run` with an API token to run the updater once.

    """

    def __init__(self, blackhole_ip, server='localhost'):
        self.blackhole_ip = blackhole_ip
        self.server = server

    def update_domains(self, domains):
        """
        Given a collection of domain names, make sure the DNS server blackholes
        those and only those domains.

        """
        raise NotImplemented

    def run(self, token):
        """
        Given a string token of the STRONGARM API, fetch the list of blackholed
        domains and run the updater.

        """

        domains = Stronglib(token).get_domains()

        failed = self.update_domains(domains)

        print "Update complete. These domains failed to update:"
        print failed


class DnsBlackholeIncrementalUpdater(DnsBlackholeUpdater):
    """
    Abstract base class to update the list of blackholes domains for a DNS
    server that adds/removes domains instead of reloading the config.

    Implements `update_domains` by taking the difference between current and
    expected domains set and adding and deleting correspondingly.

    """

    def add_domains(self, domains):
        raise NotImplemented

    def delete_domains(self, domains):
        raise NotImplemented

    def list_domains(self):
        raise NotImplemented

    def update_domains(self, domains):
        current = set(self.list_domains())
        updated = set(domains)

        return (self.add_domains(updated.difference(current)) +
                self.delete_domains(current.difference(updated)))
