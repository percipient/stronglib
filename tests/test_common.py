"""Tests for strongarm.common."""

from math import ceil
import json
import unittest

import responses
from six.moves.urllib.parse import parse_qs, urlparse

import strongarm
from strongarm.common import Struct, PaginatedResourceList


class StrongarmTestCase(unittest.TestCase):

    def test_unauthorized(self):
        """
        Test that when it's given an invalid token, stronglib raises
        unauthorized exception when making an API request.

        """

        with self.assertRaises(strongarm.StrongarmUnauthorized):
            strongarm.api_key = 'bad_token'
            strongarm.Domain.all()


class StructTestCase(unittest.TestCase):

    def test_recursive_traversal(self):
        """
        Test that the struct faithfully represent the structure of the given
        dictionary.

        """
        d = {'a': 1,
             'b': {'c': 2, 'd': 3},
             'e': {'f': {'g': ('test', 42)}},
             'h': 'value'}

        struct = Struct(d)
        self.assertEqual(struct.a, 1)
        self.assertEqual(struct.b.c, 2)
        self.assertEqual(struct.b.d, 3)
        self.assertEqual(struct.e.f.g, ('test', 42))
        self.assertEqual(struct.h, 'value')


class PaginationTestCase(unittest.TestCase):

    endpoint = 'http://example.com/integers'

    # Specification of the fake paginated API endpoint.
    total = 14
    per_page = 4
    pages = int(ceil(float(total) / per_page))

    def setUp(self):
        """
        Set up fake paginated API endpoint using responses.

        """

        def paginated_resource(request):

            params = parse_qs(urlparse(request.url).query)
            page = int(params['page'][0]) if 'page' in params else 1

            start = self.per_page * (page - 1)
            end = min(self.per_page * page, self.total)
            data = list(range(start, end))

            next_url = None
            if page < self.pages:
                next_url = '%s?page=%d' % (self.endpoint, page + 1)

            response = {'count': self.total, 'results': data, 'next': next_url}

            return (200, {}, json.dumps(response))

        responses.add_callback(responses.GET, self.endpoint,
                               callback=paginated_resource,
                               content_type='application/json')

    def lazy_pages(self, index):
        """
        How many pages the lazy list should have requested to get to index.

        """
        if index < 0:
            index += self.total
        return index // self.per_page + 1

    @responses.activate
    def test_init_lazy(self):
        """
        Test that when it's initialized, the paginated list only requests one
        page.

        """
        self.plist = PaginatedResourceList(int, self.endpoint)
        self.assertEqual(len(responses.calls), 1)

    @responses.activate
    def test_index_lazy(self):
        """
        Test that when it's being indexed, the paginated list only requests the
        pages needed.

        """
        self.plist = PaginatedResourceList(int, self.endpoint)

        self.assertEqual(self.plist[2], 2)
        self.assertEqual(len(responses.calls), self.lazy_pages(2))

        self.assertEqual(self.plist[5], 5)
        self.assertEqual(len(responses.calls), self.lazy_pages(5))

        self.assertEqual(self.plist[10], 10)
        self.assertEqual(len(responses.calls), self.lazy_pages(10))

        self.assertEqual(self.plist[13], 13)
        self.assertEqual(len(responses.calls), self.lazy_pages(13))

    @responses.activate
    def test_index_negative(self):
        """
        Test that when negative indices are handled correctly and lazily.

        """
        self.plist = PaginatedResourceList(int, self.endpoint)

        self.assertEqual(self.plist[-12], self.total - 12)
        self.assertEqual(len(responses.calls), self.lazy_pages(-12))

        self.assertEqual(self.plist[-1], self.total - 1)
        self.assertEqual(len(responses.calls), self.lazy_pages(-1))

    @responses.activate
    def test_index_out_of_bounds(self):
        """
        Test that when an out-of-bounds index is passed in, an error is thrown
        without requesting additional pages.

        """
        self.plist = PaginatedResourceList(int, self.endpoint)

        self.assertRaises(IndexError, lambda: self.plist[self.total])
        self.assertEqual(len(responses.calls), 1)

    @responses.activate
    def test_index_type_error(self):
        """
        Test that when an incorrectly typed index is passed in, an error is
        thrown without requesting additional pages.

        """
        self.plist = PaginatedResourceList(int, self.endpoint)

        self.assertRaises(TypeError, lambda: self.plist['a'])
        self.assertEqual(len(responses.calls), 1)


    @responses.activate
    def test_slice_lazy(self):
        """
        Test that when it's being sliced, the paginated list only requests the
        page needed.

        """
        self.plist = PaginatedResourceList(int, self.endpoint)

        self.assertEqual(self.plist[1:3], list(range(1, 3)))
        self.assertEqual(len(responses.calls), self.lazy_pages(2))

        self.assertEqual(self.plist[1:7:2], list(range(1, 7, 2)))
        self.assertEqual(len(responses.calls), self.lazy_pages(6))

        self.assertEqual(self.plist[10:13], list(range(10, 13)))
        self.assertEqual(len(responses.calls), self.lazy_pages(12))

    @responses.activate
    def test_list_cast(self):
        """
        Test that casting to a list makes one request per page and returns the
        entire data set provided by the endpoint.

        """
        self.plist = PaginatedResourceList(int, self.endpoint)

        entire_list = list(self.plist)
        self.assertEqual(entire_list, list(range(self.total)))
        self.assertEqual(len(responses.calls), self.lazy_pages(self.total-1))
