import sys
import pytest
import os
import json
from lib.target import Target


class TestTarget():
    def test_wrong_object(self):
        assert Target("192.167.1.1")
        with pytest.raises(AssertionError):
            assert Target(None)
            assert Target(1)

    def test_patterns(self):
        assert Target("192.167.1.1")
        assert Target("192.169.1.1")

        with pytest.raises(AssertionError):
            assert Target("169.254.169.254")
            assert Target("127.0.0.1")
            assert Target("http://github.com")

    def test_private_addresses(self):
        assert Target("192.167.1.1")
        assert Target("192.169.1.1")

        with pytest.raises(AssertionError):
            assert Target("192.168.1.1")
            assert Target("10.0.0.0.1")
            assert Target("172.16.0.0.1")

    def test_resolves_validity(self):
        assert Target("ssh.mozilla.com")
        assert Target(u'ssh.mozilla.com')
        assert Target("github.com")

        with pytest.raises(AssertionError):
            assert Target("notarealdomainname.mozilla.com")
