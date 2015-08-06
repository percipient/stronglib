from invoke import run, task

import strongarm

@task
def version():
    """Return the current version of stronglib."""
    print(strongarm.__version__)


@task
def clean():
    """Remove various build, test, and coverage artifacts."""
    run('rm -rf .tox *.egg dist build .coverage')
    run('find . -name \'__pycache__\' -delete -print -o -name \'*.pyc\' -delete -print')


@task
def build():
    """Build stronglib."""
    run('python setup.py build')


@task
def uninstall():
    """Uninstall stronglib."""
    clean()
    run('pip uninstall --yes stronglib')


@task
def uninstall_all():
    """Uninstall stronglib, dependencies, and development dependencies."""
    clean()
    run('pip uninstall --yes -r requirements.txt')


@task
def test():
    """Run stronglib unittests."""
    run('python setup.py test')


@task
def test_tox():
    """Run tests with tox."""
    run('tox')


@task
def test_sdist():
    """Test sdist build and install."""
    clean()
    run('python setup.py sdist')
    run('pip install --force-reinstall --upgrade dist/*.gz')


@task
def test_bdist_wheel():
    """Test building bdist wheel and install."""
    clean()
    run('python setup.py bdist_wheel')
    run('pip install --force-reinstall --upgrade dist/*.whl')


@task
def test_dist():
    """Test both sdist and bdist wheel and install."""
    test_sdist()
    test_bdist_wheel()


@task
def test_all():
    """Run all tests; unit, tox, dist."""
    test()
    test_tox()
    test_dist()
