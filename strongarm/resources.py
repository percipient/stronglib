from strongarm.common import (CreatableResource, DeletableResource,
                              ListableResource, StrongResource)


class Domain(StrongResource, CreatableResource, DeletableResource, ListableResource):
    endpoint = '/api/domains/'

    # The domain name is used as the unique identifier passed in the url.
    id_attr = 'name'


class Infection(StrongResource, ListableResource):
    endpoint = '/api/infections/'
