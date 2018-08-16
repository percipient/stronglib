import json

import requests
from six import integer_types, iteritems
from six.moves import xrange

import strongarm


class StrongarmException(Exception):
    """
    An error occured in stronglib.

    """


class StrongarmHttpError(StrongarmException):
    """
    The strongarm.io API responded with an HTTP error code.

    """

    def __init__(self, status_code, detail):
        super(StrongarmHttpError, self).__init__(status_code, detail)

        self.status_code = status_code
        self.detail = detail


class StrongarmUnauthorized(StrongarmHttpError):
    """
    Missing or incorrect authentication credentials.

    """

    def __init__(self, msg):
        super(StrongarmUnauthorized, self).__init__(requests.codes.unauthorized,
                                                    msg)


def request(method, endpoint, **kwargs):
    """
    Wrap requests.request to help make HTTP requests to the API.

    Add authentication to request and do error checking on response.

    """

    if 'headers' not in kwargs:
        kwargs['headers'] = {}

    # Add authorization token to the request headers.
    kwargs['headers']['Authorization'] = 'Token %s' % strongarm.api_key

    # Explicitly specify the API version for future-proofing.
    kwargs['headers']['Accept'] = ('application/json; version=%s' %
                                   strongarm.api_version)

    # Don't allow requests to follow redirects, it is generally bad practice to
    # allow an API library to follow any redirects.
    kwargs['allow_redirects'] = False

    # This should only be used for development, never in a production
    # environment.
    if strongarm._ignore_certificates is True:
       kwargs['verify'] = False

    res = requests.request(method, endpoint, **kwargs)

    # Raise StrongarmUnauthorized for HTTP 401 Unauthorized.
    if res.status_code == requests.codes.unauthorized:
        try:
            msg = res.json()['detail']
        except (ValueError, KeyError):
            msg = res.text
        raise StrongarmUnauthorized(msg)

    # Raise StrongarmException for HTTP error codes.
    elif res.status_code >= 400:
        try:
            msg = res.json()['detail']
        except (ValueError, KeyError, TypeError):
            msg = res.text
        raise StrongarmHttpError(res.status_code, msg)

    # If the content is empty, do not parse json and return None directly.
    if not res.text:
        return None

    try:
        return res.json()
    # If the content is not json, raise StrongarmException.
    except ValueError:
        raise StrongarmException("Failed to parse response: %s" % res.text)


class PaginatedResourceList(object):
    """
    A read-only list replacement for supporting pagination of the strongarm.io API.

    Given a resource endpoint URL, get the first page on initialization and
    then lazily get the rest when needed.

    Calling `len()` on the object reports the total number of elements, even if
    some of them are not yet fetched into memory.

    Provide a custom iterator that loops over all elements, transparently
    fetching additional pages when needed. Indexing and slicing work similarly.

    """

    def __init__(self, content_cls, first_url, params=None):
        self.__content_cls = content_cls
        self.__data = []
        self.__len = None
        self.__next_url = first_url
        # The first time we expand we can pass in additional parameters (e.g.
        # for filtering).
        self.__expand(params=params)

    def __can_expand(self):
        """
        Whether or not there are additional pages of data to fetch.

        """
        return len(self.__data) < self.__len

    def __expand(self, **kwargs):
        """
        Expand the internal list by fetching an additional page of data.

        """
        data = request('get', self.__next_url, **kwargs)

        if self.__len is None:
            self.__len = data['count']

        self.__next_url = data.get('next')

        new_data = [self.__content_cls(element) for element in data['results']]
        self.__data += new_data

        return new_data

    def __len__(self):
        return self.__len

    def __iter__(self):
        for element in self.__data:
            yield element

        while self.__can_expand():
            new_data = self.__expand()
            for element in new_data:
                yield element

    def __getitem__(self, index):

        if isinstance(index, integer_types):
            if index < 0:
                index += self.__len

            if not (0 <= index < self.__len):
                raise IndexError("list index out of range")

            while index >= len(self.__data):
                self.__expand()

            return self.__data[index]

        elif isinstance(index, slice):
            # Since indexing is lazily implemented above, slicing is simply
            # implemented by looping over indices covered by the slice.
            # See https://docs.python.org/2.3/whatsnew/section-slices.html
            # on the awesome indices(length) method on slice objects.
            return [self[i] for i in xrange(*index.indices(len(self)))]

        raise TypeError("list indices must be integers, not %s" % type(index))

    def count():
        return self.__len


class Struct(object):
    """
    A generic object providing dot notation on dictionaries.

    """

    def __init__(self, dictionary):

        self.__dict__.update(dictionary)

        for k, v in iteritems(self.__dict__):
            if isinstance(v, dict):
                self.__dict__[k] = Struct(v)

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, self.__dict__)


class StrongResource(Struct):
    """
    The abstract base class for a piece of a resource.

    Support the `get` method that takes an id and gets a single instance of the
    resource from the API.

    Implementations should define a class variable `endpoint` to specify the
    API path.

    """

    @classmethod
    def get(cls, id):
        endpoint = strongarm.host + cls.endpoint + str(id)
        if not endpoint.endswith('/'):
            endpoint = endpoint + '/'
        return cls(request('get', endpoint))


class ListableResource(object):
    """
    A mixin for a resource that can be listed.

    The `all` method returns an instance of PaginatedResourceList that lazily
    contains all instances of the requested resource.

    """
    id_attr = None

    @classmethod
    def all(cls):
        endpoint = strongarm.host + cls.endpoint
        return PaginatedResourceList(cls, endpoint)


class FilterableResource(ListableResource):
    """
    A mixin for a resource that can be filtered when being listed.
    """
    filterable_attrs = None

    @classmethod
    def filter(cls, **kwargs):
        # Ensure each filter request is valid.
        unknown_filters = set(kwargs.keys()) - set(cls.filterable_attrs)
        if unknown_filters:
            raise ValueError('Unknown filters added: {}'.format(', '.join(unknown_filters)))

        endpoint = strongarm.host + cls.endpoint
        return PaginatedResourceList(cls, endpoint, params=kwargs)


class CreatableResource(object):
    """
    A mixin for a resource that can be created.

    The `create` method returns an instance of the newly created resource.

    """

    @classmethod
    def create(cls, **kwargs):
        endpoint = strongarm.host + cls.endpoint
        return cls(request('post', endpoint, data=json.dumps(kwargs),
                           headers={'Content-Type': 'application/json'}))


class DeletableResource(object):
    """
    A mixin for a resource that can be deleted.

    The `delete` method returns None on successful deletion.

    """

    # The attribute to be used as the unique identifier.
    id_attr = 'id'

    def delete(self, **kwargs):
        endpoint = strongarm.host + self.endpoint + str(getattr(self, self.id_attr))
        if not endpoint.endswith('/'):
            endpoint = endpoint + '/'
        request('delete', endpoint)
