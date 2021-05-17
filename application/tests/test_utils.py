from application.exceptions import LoginNotCompleted
from application.utils import check_auth_and_wait_load_delay
import pytest
from unittest import mock


@check_auth_and_wait_load_delay
def smart_function(self):
    return 1 + 1


@mock.patch("application.utils.time")
def test_auth_decorator_for_logged_users(_timemock):
    self = mock.Mock(logged_in=True)
    result = smart_function(self)
    assert _timemock.sleep.called
    assert result == 2


@mock.patch("application.utils.time")
def test_auth_decorator_for_not_logged_users(_timemock):
    self = mock.Mock(logged_in=False)

    with pytest.raises(LoginNotCompleted):
        smart_function(self)

    assert not _timemock.sleep.called
