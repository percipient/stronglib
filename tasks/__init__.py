from invoke import run, task

import strongarm

@task
def version(ctx):
    """Return the current version of stronglib."""
    print(strongarm.__version__)


@task
def clean(ctx):
    """Remove various build, test, and coverage artifacts."""
    run('rm -rf .tox *.egg dist build .coverage')
    run('find . -name \'__pycache__\' -delete -print -o -name \'*.pyc\' -delete -print')


@task
def build(ctx):
    """Build stronglib."""
    run('python setup.py build')


@task
def uninstall(ctx):
    """Uninstall stronglib."""
    clean(ctx)
    run('pip uninstall --yes stronglib')


@task
def uninstall_all(ctx):
    """Uninstall stronglib, dependencies, and development dependencies."""
    clean(ctx)
    run('pip uninstall --yes -r requirements.txt')


@task
def test(ctx):
    """Run stronglib unittests."""
    run('python setup.py test')


@task
def test_tox(ctx):
    """Run tests with tox."""
    run('tox')


@task
def test_sdist(ctx):
    """Test sdist build and install."""
    clean(ctx)
    run('python setup.py sdist')
    run('pip install --force-reinstall --upgrade dist/*.gz')


@task
def test_bdist_wheel(ctx):
    """Test building bdist wheel and install."""
    clean(ctx)
    run('python setup.py bdist_wheel')
    run('pip install --force-reinstall --upgrade dist/*.whl')


@task
def test_dist(ctx):
    """Test both sdist and bdist wheel and install."""
    test_sdist(ctx)
    test_bdist_wheel(ctx)


@task
def test_all(ctx):
    """Run all tests; unit, tox, dist."""
    test(ctx)
    test_tox(ctx)
    test_dist(ctx)
