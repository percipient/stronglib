import requests


class StronglibException(Exception):
    """
    An error occured in stronglib.

    """


class StronglibUnauthorized(StronglibException):
    """
    Missing or incorrect authentication credentials.

    """


class Stronglib(object):

    DEFAULT_HOST = 'https://strongarm.percipientnetworks.com'

    def __init__(self, token, host=None):
        self.token = token
        self.host = host if host else self.DEFAULT_HOST

    def _request(self, endpoint, headers=None, params=None):
        if headers is None:
            headers = {}

        # Add authorization token to the request headers.
        headers.update({'Authorization': 'Token %s' % self.token})

        res = requests.get(endpoint, headers=headers, params=params)

        if res.status_code == 401:
            try:
                msg = res.json()['details']
            except KeyError:
                msg = ''
            raise StronglibUnauthorized(msg)

        elif res.status_code != requests.codes.ok:
            raise StronglibException("Received error code %d" % res.status_code)

        res_json = res.json()

        if 'results' not in res_json:
            raise StronglibException("Unknown response: %s" % res_json)

        return res_json['results']

    def get_domains(self):
        endpoint = self.host + '/api/domains/'
        return [domain['name'] for domain in self._request(endpoint)]
