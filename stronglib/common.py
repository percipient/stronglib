import requests

import stronglib


class StronglibException(Exception):
    """
    An error occured in stronglib.

    """


class StronglibUnauthorized(StronglibException):
    """
    Missing or incorrect authentication credentials.

    """


def request(method, endpoint, **kwargs):
    """
    Wrap requests.request to help make HTTP requests to STRONGARM API.

    Add authentication to request and do error checking on response.

    """

    # Add authorization token to the request headers.
    if 'headers' not in kwargs:
        kwargs['headers'] = {}
    kwargs['headers']['Authorization'] = 'Token %s' % stronglib.api_key

    res = requests.request(method, endpoint, **kwargs)

    # Raise Stronglib exceptions on the error code.
    if res.status_code == 401:
        try:
            msg = res.json()['details']
        except KeyError:
            msg = ''
        raise StronglibUnauthorized(msg)

    elif res.status_code != requests.codes.ok:
        raise StronglibException("Received error code %d" % res.status_code)

    return res.json()


class PaginatedResourceList(object):
    """
    A list replacement for supporting the pagination of STRONGARM API.

    Given a resource endpoint URL, it fetches the first page on initialization,
    and then lazily fetches the rest when needed.

    Calling `len()` on the object reports the total number of elements, even if
    some of them are not yet fetched into memory.

    Provide a custom iterator that loops over all elements, transparently
    fetching additional pages when needed. Indexing and slicing work similarly.

    """

    def __init__(self, contentClass, firstUrl):
        self.__contentClass = contentClass
        self.__data = []
        self.__len = None
        self.__nextUrl = firstUrl
        self.__expand()

    def __can_expand(self):
        return len(self._data) < self.__len

    def __expand(self):
        data = request('get', self.__nextUrl)

        if self.__len is None:
            self.__len = data['count']

        self.__nextUrl = data.get('next')

        newData = [self.__contentClass(element) for element in data['results']]
        self.__data += newData

        return newData

    def __len__(self):
        return self.__len

    def __iter__(self):
        for element in self.__data:
            yield element

        while self.__can_expand():
            newData = self.__expand()
            for element in newData:
                yield element

    def __getitem__(self, index):

        if isinstance(index, (int, long)):
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


class StrongResource(dict):
    """
    The abstract base class for a piece of STRONGARM resource.

    Support the `retrieve` method that takes an id and gets a single instance
    of the resource from the API.

    Implementations should define a class variable `endpoint` to specifie the
    API path.

    """

    @classmethod
    def retrieve(cls, id):
        endpoint = stronglib.host + cls.endpoint + str(id)
        return cls(request('get', endpoint))


class ListableResource(object):
    """
    A mixin for a STRONGARM resource that can be listed.

    The `list` method returns an instance of PaginatedList that lazily contains
    all instances of the requested resource.

    """

    @classmethod
    def list(cls):
        endpoint = stronglib.host + cls.endpoint
        return PaginatedResourceList(cls, endpoint)
