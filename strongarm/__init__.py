"""
stronglib - a Python library for the STRONGARM API

"""


__author__ = 'Percipient Networks, LLC'
__version__ = '0.1.0'
__license__ = 'Apache 2.0'


host = 'https://strongarm.percipientnetworks.com'
api_key = None


from strongarm.common import (StrongarmException, StrongarmHttpError,
                              StrongarmUnauthorized)
from strongarm.resources import Domain
