try:
    from unittest import mock
except ImportError:
    import mock
import pytest

from . import contexts


@pytest.yield_fixture
def user_override():
    """
    Override site.USER_BASE and site.USER_SITE with temporary directories in
    a context.
    """
    with contexts.tempdir() as user_base:
        with mock.patch('site.USER_BASE', user_base):
            with contexts.tempdir() as user_site:
                with mock.patch('site.USER_SITE', user_site):
                    with contexts.save_user_site_setting():
                        yield


@pytest.yield_fixture
def tmpdir_cwd(tmpdir):
    with tmpdir.as_cwd() as orig:
        yield orig
