"""Tests for strongarm.common."""

from math import ceil
import json
import unittest

import responses
from six.moves.urllib.parse import parse_qs, urlparse

import strongarm
from strongarm.common import request, Struct, PaginatedResourceList


class RequestTestCase(unittest.TestCase):

    # The mocked url to make test requests to.
    url = 'http://example.com/api/domains/'

    @responses.activate
    def test_authorization(self):
        """
        Test that when it's given an invalid token, stronglib raises
        unauthorized exception when making an API request.

        """

        token = "this_is_a_token"
        unauth_msg = "Get out of here!"
        data = {'data': 'some_data'}

        def authorization_required(request):

            if not ('Authorization' in request.headers and
                    request.headers['Authorization'] == 'Token %s' % token):
                return (401, {}, json.dumps({'detail': unauth_msg}))

            return (200, {}, json.dumps(data))

        responses.add_callback(responses.GET, self.url,
                               callback=authorization_required,
                               content_type='application/json')

        # If a wrong token is provided:
        with self.assertRaises(strongarm.StrongarmUnauthorized) as exp:
            strongarm.api_key = 'bad_token'
            request('get', self.url)
        self.assertEqual(401, exp.exception.status_code)
        self.assertEqual(unauth_msg, exp.exception.detail)

        # If the correct token is provided:
        strongarm.api_key = token
        self.assertEqual(request('get', self.url), data)

    @responses.activate
    def test_version_header(self):
        """
        Test that the API version is explicitly included in the Accept header.

        """

        correct_header = 'application/json; version=1.0'

        def assert_header(request):

            self.assertIn('Accept', request.headers)
            self.assertEqual(request.headers['Accept'], correct_header)

            return (200, {}, '')

        responses.add_callback(responses.GET, self.url,
                               callback=assert_header,
                               content_type='application/json')

        # Make a random request to trigger the test in the above callback.
        request('get', self.url)

    @responses.activate
    def test_error_code_msg(self):
        """
        Test that when an HTTP error code is received, StrongarmHttpError is
        raised with the status code and the provided error message.

        """

        msg = "Something something does not exist."

        responses.add(responses.GET, self.url, status=404,
                      content_type='application/json',
                      body=json.dumps({'detail': msg}))

        with self.assertRaises(strongarm.StrongarmHttpError) as exp:
            request('get', self.url)

        self.assertEqual(exp.exception.status_code, 404)
        self.assertEqual(exp.exception.detail, msg)

    @responses.activate
    def test_error_code_no_json(self):
        """
        Test that when an HTTP error code is received with non-json data,
        StrongarmHttpError is raised with the status code and the raw data.

        """

        msg = "<h1>Bad request</h1>"

        responses.add(responses.GET, self.url, status=400,
                      content_type='text/html', body=msg)

        with self.assertRaises(strongarm.StrongarmHttpError) as exp:
            request('get', self.url)

        self.assertEqual(exp.exception.status_code, 400)
        self.assertEqual(exp.exception.detail, msg)

    @responses.activate
    def test_no_content(self):
        """
        Test that when the request does not have any content, None is returned.

        """

        responses.add(responses.GET, self.url, status=204,
                      content_type='application/json')

        self.assertIsNone(request('get', self.url))

    @responses.activate
    def test_parse_error(self):
        """
        Test that when the request is not json, StrongarmException is raised.

        """

        responses.add(responses.GET, self.url, status=200,
                      content_type='text/html', body='text')

        with self.assertRaises(strongarm.StrongarmException) as exp:
            request('get', self.url)


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
