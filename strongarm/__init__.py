"""
stronglib - a Python library for the STRONGARM API

"""


__author__ = 'Percipient Networks, LLC'
__version__ = '0.1.2'
__license__ = 'Apache 2.0'


host = 'https://strongarm.io'
api_key = None
api_version = '0.1.0'  # Developers generally should not change this.


from strongarm.common import (StrongarmException, StrongarmHttpError,
                              StrongarmUnauthorized)
from strongarm.resources import Domain
