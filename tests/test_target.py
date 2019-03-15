import sys
import pytest
import os
import json
from lib.target import Target


class TestTarget():
    def test_wrong_object(self):
        target = Target("192.167.1.1")
        assert target.name == "192.167.1.1"

        with pytest.raises(AssertionError):
            assert Target(None)
            assert Target(1)

    def test_patterns(self):
        target = Target("192.167.1.1")
        assert target.name == "192.167.1.1"

        with pytest.raises(AssertionError):
            assert Target("169.254.169.254")
            assert Target("127.0.0.1")
            assert Target("http://github.com")

    def test_private_addresses(self):
        target = Target("192.167.1.1")
        assert target.name == "192.167.1.1"

        target = Target("192.169.1.1")
        assert target.name == "192.169.1.1"

        with pytest.raises(AssertionError):
            assert Target("192.168.1.1")
            assert Target("10.0.0.0.1")
            assert Target("172.16.0.0.1")

    def test_resolves_validity(self):
        target = Target("ssh.mozilla.com")
        assert target.name == "ssh.mozilla.com"
        target = Target(u'ssh.mozilla.com')
        assert target.name == u'ssh.mozilla.com'
        target = Target("github.com")
        assert target.name == "github.com"

        with pytest.raises(AssertionError):
            assert Target("notarealdomainname.mozilla.com")
