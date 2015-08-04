"""
stronglib - a Python library for the STRONGARM API

"""


__author__ = 'Percipient Networks, LLC'
__version__ = 'dev'
__licence__ = 'Apache 2.0'


host = 'https://strongarm.percipientnetworks.com'
api_key = None


from stronglib.common import (StronglibException, StronglibUnauthorized)
from stronglib.resources import Domain
