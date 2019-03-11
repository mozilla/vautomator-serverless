import sys
import pytest
import os
import json
from lib.target import Target


class TestTarget():
    def test_null_validity(self):
        target = Target(None)
        assert target.isValid() is False

    def test_loopback_validity(self):
        target = Target("127.0.0.1")
        assert target.isValid() is False

    def test_magic_url_validity(self):
        target = Target("169.254.169.254")
        assert target.isValid() is False

    def test_private_addresses(self):
        target = Target("192.167.1.1")
        assert target.isValid() is True
        target = Target("192.168.1.1")
        assert target.isValid() is False
        target = Target("192.169.1.1")
        assert target.isValid() is True
        target = Target("10.0.0.0.1")
        assert target.isValid() is False
        target = Target("172.16.0.0.1")
        assert target.isValid() is False

    def test_resolves_validity(self):
        target = Target("ssh.mozilla.com")
        assert target.isValid() is True
        target = Target("notarealdomainname.mozilla.com")
        assert target.isValid() is False
        target = Target(u"notarealdomainname.mozilla.com")
        assert target.isValid() is False
        target = Target("ssh.mozilla.com")
        assert target.isValid() is True
        target = Target(u'ssh.mozilla.com')
        assert target.isValid() is True
        target = Target("github.com")
        assert target.isValid() is True
