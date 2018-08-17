from strongarm.common import (CreatableResource,
                              DeletableResource,
                              FilterableResource,
                              ListableResource,
                              StrongResource)


class Domain(StrongResource, CreatableResource, DeletableResource, FilterableResource):
    endpoint = '/api/domains/'

    # The domain name is used as the unique identifier passed in the url.
    id_attr = 'name'
    filterable_attrs = ['statuses']

    # Constants for use with the status field.
    # A blacklisted domain will be redirected to the Strongarm blackhole when
    # queried. Strongarm users will be sent an alert when a user attempts to
    # visit a blacklisted domain.
    BLACKLISTED = 'blacklisted'
    # A whitelisted domain will always recursively resolve, even if the domain
    # is blocked based on one of the Strongarm feeds or due to content filtering
    # policy.
    WHITELISTED = 'whitelisted'
    # A filtered domain will be blocked for content filtering.
    FILTERED = 'filtered'


class Infection(StrongResource, ListableResource):
    endpoint = '/api/infections/'
