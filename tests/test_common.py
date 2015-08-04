"""Tests for strongarm.common."""

from math import ceil
import json
import unittest
from urlparse import parse_qs, urlparse

import responses

import strongarm
from strongarm.common import PaginatedResourceList


class StrongarmTestCase(unittest.TestCase):

    def test_unauthorized(self):
        """
        Test that when it's given an invalid token, stronglib raises
        unauthorized exception when making an API request.

        """

        with self.assertRaises(strongarm.StrongarmUnauthorized):
            strongarm.api_key = 'bad_token'
            strongarm.Domain.all()


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

            data = range(self.per_page * (page - 1),
                         min(self.per_page * page, self.total))

            next_url = None
            if page < self.pages:
                next_url = '%s?page=%d' % (self.endpoint, page + 1)

            response = {'count': self.total, 'results': data, 'next': next_url}

            return (200, {}, json.dumps(response))

        responses.add_callback(responses.GET, self.endpoint,
                               callback=paginated_resource,
                               content_type='application/json')

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
        self.assertEqual(len(responses.calls), 1)

        self.assertEqual(self.plist[5], 5)
        self.assertEqual(len(responses.calls), 2)

        self.assertEqual(self.plist[10], 10)
        self.assertEqual(len(responses.calls), 3)

        self.assertEqual(self.plist[13], 13)
        self.assertEqual(len(responses.calls), 4)

    @responses.activate
    def test_index_error(self):
        """
        Test that when an out-of-bounds index is passed in, an error is thrown
        without requesting additional pages.

        """
        self.plist = PaginatedResourceList(int, self.endpoint)

        self.assertRaises(IndexError, lambda: self.plist[self.total])
        self.assertEqual(len(responses.calls), 1)

    @responses.activate
    def test_slice_lazy(self):
        """
        Test that when it's being sliced, the paginated list only requests the
        page needed.

        """
        self.plist = PaginatedResourceList(int, self.endpoint)

        self.assertEqual(self.plist[1:3], range(1, 3))
        self.assertEqual(len(responses.calls), 1)

        self.assertEqual(self.plist[1:7:2], range(1, 7, 2))
        self.assertEqual(len(responses.calls), 2)

        self.assertEqual(self.plist[10:13], range(10, 13))
        self.assertEqual(len(responses.calls), 4)

    @responses.activate
    def test_list_cast(self):
        """
        Test that casting to a list makes one request per page and returns the
        entire data set provided by the endpoint.

        """
        self.plist = PaginatedResourceList(int, self.endpoint)

        entire_list = list(self.plist)
        self.assertEqual(entire_list, range(self.total))
        self.assertEqual(len(responses.calls), 4)
