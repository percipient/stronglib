"Tests for strongarm.resources."""

import json
import unittest

import responses

import strongarm
from strongarm.resources import Domain, Infection


class DomainTestCase(unittest.TestCase):

    list_response = {
        "count": 5,
        "next": None,
        "previous": None,
        "results": [
            {
                "name": "0.example.com",
                "user": "malwaredomainlist",
                "date": "2015-08-05T18:19:14Z"
            },
            {
                "name": "1.example.com",
                "user": "zeustracker",
                "date": "2015-07-28T16:22:39Z"
            },
            {
                "name": "2.example.com",
                "user": "malwaredomainlist",
                "date": "2015-07-28T16:23:41Z"
            },
            {
                "name": "3.example.com",
                "user": "malwaredomainlist",
                "date": "2015-07-28T16:22:57Z"
            },
            {
                "name": "example.org",
                "user": "malwaredomainlist",
                "date": "2015-07-28T16:22:55Z"
            }
        ]
    }

    get_response = {
        "name": "0.example.com",
        "user": "malwaredomainlist",
        "date": "2015-08-05T18:19:14Z"
    }

    @responses.activate
    def test_list(self):
        """
        Test that getting all domains returns a PaginatedResourceList with the
        right elements.

        """

        responses.add(responses.GET, strongarm.host + Domain.endpoint,
                      body=json.dumps(self.list_response),
                      content_type='application/json')

        domains = Domain.all()

        self.assertEqual(len(responses.calls), 1)

        self.assertEqual(len(domains), self.list_response['count'])
        self.assertIsInstance(domains[0], Domain)
        self.assertEqual(domains[0].name, self.list_response['results'][0]['name'])

    @responses.activate
    def test_get_exists(self):
        """
        Test that getting an existing blackholed domain returns an instance of
        Domain with the right attributes.

        """

        name = self.get_response['name']

        responses.add(responses.GET, strongarm.host + Domain.endpoint + name + '/',
                      body=json.dumps(self.get_response),
                      content_type='application/json/')

        domain = Domain.get(name)

        self.assertEqual(len(responses.calls), 1)

        self.assertIsInstance(domain, Domain)
        self.assertEqual(domain.name, name)

    @responses.activate
    def test_get_not_found(self):
        """
        Test that getting a non-existent domain raises a StrongarmHttpError.

        """

        name = 'non-existent.example.com'
        msg = 'The domain does not exist.'

        responses.add(responses.GET, strongarm.host + Domain.endpoint + name + '/',
                      status=404, content_type='application/json',
                      body=json.dumps({'detail': msg}))

        with self.assertRaises(strongarm.StrongarmHttpError) as exp:
            Domain.get(name)

        self.assertEqual(len(responses.calls), 1)

        self.assertEqual(exp.exception.status_code, 404)
        self.assertEqual(exp.exception.detail, msg)

    @responses.activate
    def test_create(self):
        """
        Test that creating a new blackholed domain returns an instance of
        Domain with the right attributes.

        """

        name = self.get_response['name']

        responses.add(responses.POST, strongarm.host + Domain.endpoint,
                      body=json.dumps(self.get_response),
                      content_type='application/json')

        domain = Domain.create(name=name)

        self.assertEqual(len(responses.calls), 1)

        self.assertIsInstance(domain, Domain)
        self.assertEqual(domain.name, name)

    @responses.activate
    def test_delete_success(self):
        """
        Test that deleting a domain succeeds silently.

        """

        name = self.get_response['name']

        responses.add(responses.GET, strongarm.host + Domain.endpoint + name + '/',
                      body=json.dumps(self.get_response),
                      content_type='application/json/')
        responses.add(responses.DELETE, strongarm.host + Domain.endpoint + name + '/',
                      status=204)

        # First get the domain to be deleted
        domain = Domain.get(name)

        self.assertEqual(len(responses.calls), 1)

        # Now delete the domain.
        result = domain.delete()

        self.assertEqual(len(responses.calls), 2)
        self.assertIsNone(result)

    @responses.activate
    def test_delete_not_found(self):
        """
        Test that deleting a non-existent domain raises StrongarmHttpError.

        """

        name = 'non-existent.example.com'

        responses.add(responses.DELETE, strongarm.host + Domain.endpoint + name + '/',
                      status=404)

        # Create the Domain instance manually.
        domain = Domain({'name': name})

        # Now delete the domain.
        with self.assertRaises(strongarm.StrongarmHttpError) as exp:
            domain.delete()

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(exp.exception.status_code, 404)


class InfectionTestCase(unittest.TestCase):

    list_response = {
        "count": 2,
        "next": None,
        "previous": None,
        "results": [
            {
                "id": "MgEqqxrm",
                "port": 80,
                "victim_ip": "1.2.3.4",
                "victim_hostname": None,
                "dest_domain": "0.example.com",
                "first_seen": "2016-01-15T20:42:33Z",
                "last_seen": "2016-01-15T20:45:17Z",
                "resolved": False,
                "protocol": "http"
            },
            {
                "id": "l3JPB8fo",
                "port": 6667,
                "victim_ip": "1.2.3.4",
                "victim_hostname": None,
                "dest_domain": None,
                "first_seen": "2016-01-15T20:41:56Z",
                "last_seen": "2016-01-15T20:42:19Z",
                "resolved": False,
                "protocol":"irc"
            }
        ]
    }

    get_response = {
        "id": "MgEqqxrm",
        "port": 80,
        "victim_ip": "1.2.3.4",
        "victim_hostname": None,
        "dest_domain": "0.example.com",
        "first_seen": "2016-01-15T20:42:33Z",
        "last_seen": "2016-01-15T20:45:17Z",
        "resolved": False,
        "protocol": "http"
    }

    @responses.activate
    def test_list(self):
        """
        Test that getting all infections returns a PaginatedResourceList with
        the right elements.

        """

        responses.add(responses.GET, strongarm.host + Infection.endpoint,
                      body=json.dumps(self.list_response),
                      content_type='application/json')

        infections = Infection.all()

        self.assertEqual(len(responses.calls), 1)

        self.assertEqual(len(infections), self.list_response['count'])
        self.assertIsInstance(infections[0], Infection)
        self.assertEqual(infections[0].id, self.list_response['results'][0]['id'])

    @responses.activate
    def test_get_exists(self):
        """
        Test that getting an infection returns an instance of Infection with the
        right attributes.

        """

        id = self.get_response['id']

        responses.add(responses.GET, strongarm.host + Infection.endpoint + id + '/',
                      body=json.dumps(self.get_response),
                      content_type='application/json/')

        infection = Infection.get(id)

        self.assertEqual(len(responses.calls), 1)

        self.assertIsInstance(infection, Infection)
        self.assertEqual(infection.id, id)

    @responses.activate
    def test_get_not_found(self):
        """
        Test that getting a non-existent infection raises a StrongarmHttpError.

        """

        id = 'does-not-exist'
        msg = 'Not found.'

        responses.add(responses.GET, strongarm.host + Infection.endpoint + id + '/',
                      status=404, content_type='application/json',
                      body=json.dumps({'detail': msg}))

        with self.assertRaises(strongarm.StrongarmHttpError) as exp:
            Infection.get(id)

        self.assertEqual(len(responses.calls), 1)

        self.assertEqual(exp.exception.status_code, 404)
        self.assertEqual(exp.exception.detail, msg)

    @responses.activate
    def test_create(self):
        """
        Test that Infection does not have a create attribute.

        """

        self.assertFalse(hasattr(Infection, 'create'))

    @responses.activate
    def test_delete_success(self):
        """
        Test that an Infection instance does not have a delete attribute.

        """
        id = self.get_response['id']

        responses.add(responses.GET, strongarm.host + Infection.endpoint + id + '/',
                      body=json.dumps(self.get_response),
                      content_type='application/json/')

        # Get the infection to be 'deleted'.
        infection = Infection.get(id)

        self.assertEqual(len(responses.calls), 1)

        self.assertIsInstance(infection, Infection)

        # Deletion is not possible.
        self.assertFalse(hasattr(infection, 'delete'))
