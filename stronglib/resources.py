from stronglib.common import StrongResource, ListableResource


class Domain(StrongResource, ListableResource):
    endpoint = '/api/domains/'
