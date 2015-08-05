from strongarm.common import (CreatableResource, ListableResource,
                              StrongResource)


class Domain(StrongResource, ListableResource, CreatableResource):
    endpoint = '/api/domains/'
