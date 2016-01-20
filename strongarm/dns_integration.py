import strongarm


class DnsBlackholeUpdaterException(strongarm.StrongarmException):
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

        Return a list of domains that failed to update.

        """
        raise NotImplementedError

    def run(self, token):
        """
        Given a string token for the API, fetch the list of blackholed
        domains and run the updater.

        Return a list of domains that failed to update.

        """

        strongarm.api_key = token

        # Use a generator expression to ensure domain pages are lazily fetched
        # as they are being processed in `update_domains`.
        domains = (domain.name for domain in strongarm.Domain.all())

        return self.update_domains(domains)


class DnsBlackholeIncrementalUpdater(DnsBlackholeUpdater):
    """
    Abstract base class to update the list of blackholes domains for a DNS
    server that adds/removes domains instead of reloading the config.

    Implements `update_domains` by taking the difference between current and
    expected domains set and adding and deleting correspondingly.

    Each DNS server integration should subclass and implement `add_domains`,
    `delete_domains`, and `list_domains`.

    """

    def add_domains(self, domains):
        """
        Add the given collection of domains to the blackhole.

        Return a list of domains names that failed to be added.

        """
        raise NotImplementedError

    def remove_domains(self, domains):
        """
        Remove the given collection of domains from the blackhole.

        Return a list of domains names that failed to be removed.

        """
        raise NotImplementedError

    def list_domains(self):
        """
        Return a list of domains that are currently blackholed.

        """
        raise NotImplementedError

    def update_domains(self, domains):
        current = set(self.list_domains())
        updated = set(domains)

        return (self.add_domains(updated.difference(current)) +
                self.remove_domains(current.difference(updated)))
