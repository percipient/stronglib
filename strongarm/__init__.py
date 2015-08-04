"""
stronglib - a Python library for the STRONGARM API

"""


__author__ = 'Percipient Networks, LLC'
__version__ = 'dev'
__license__ = 'Apache 2.0'


host = 'https://strongarm.percipientnetworks.com'
api_key = None


from strongarm.common import (StrongarmException, StrongarmUnauthorized)
from strongarm.resources import Domain
