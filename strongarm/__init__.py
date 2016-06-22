"""
stronglib - a Python library for the strongarm.io API

"""


__author__ = 'Percipient Networks, LLC'
__version__ = '0.1.5'
__license__ = 'Apache 2.0'


host = 'https://app.strongarm.io'
api_key = None
api_version = '0.1.0'  # Developers generally should not change this.

# This should never be set to True in a production environment and exists purely
# for testing.
_ignore_certificates = False

from strongarm.common import (StrongarmException, StrongarmHttpError,
                              StrongarmUnauthorized)
from strongarm.resources import Domain, Infection
