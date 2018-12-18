import re
import sys
import codecs

from setuptools import setup, find_packages


install_requires = [
    'requests==2.21.0',
    'six==1.11.0',
]


def version():
    # Get version without importing the module.
    with open('strongarm/__init__.py', 'r') as fd:
        return re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                         fd.read(), re.MULTILINE).group(1)


def long_description():
    with codecs.open('README.rst', encoding='utf8') as f:
        return f.read()

setup(
    name='stronglib',
    version=version(),
    description='A Python library for strongarm.io API',
    long_description=long_description(),
    url='https://dnswatch.watchguard.com',
    download_url='https://github.com/percipient/stronglib',
    author='Percipient Networks, LLC',
    author_email='support@strongarm.io',
    license='Apache 2.0',
    packages=find_packages(),
    install_requires=install_requires,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries',
        'Topic :: System :: Networking',
    ],
)
