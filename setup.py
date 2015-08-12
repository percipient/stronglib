import re
import sys
import codecs

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand


class PyTest(TestCommand):
    # `$ python setup.py test' simply installs minimal requirements
    # and runs the tests with no fancy stuff like parallel execution.
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = [
            '--cov', './strongarm',
            '--doctest-modules', '--verbose',
            './tests'
        ]
        self.test_suite = True

    def run_tests(self):
        import pytest
        sys.exit(pytest.main(self.test_args))


tests_require = [
    'pytest>=2.6.4',
    'pytest-cov==1.8.1',
    'responses==0.4.0',
]


install_requires = [
    'requests==2.7.0',
    'six==1.9.0',
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
    description='A Python library for STRONGARM API',
    long_description=long_description(),
    url='http://strongarm.io/',
    download_url='https://github.com/percipient/stronglib',
    author='Percipient Networks, LLC',
    author_email='support@percipientnetworks.com',
    license='Apache 2.0',
    packages=find_packages(),
    install_requires=install_requires,
    tests_require=tests_require,
    cmdclass={'test': PyTest},
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries',
        'Topic :: System :: Networking',
    ],
)
