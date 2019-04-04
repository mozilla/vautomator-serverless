import sys
import pytest
import os
import json
from lib.hosts import Hosts


class TestHosts():
    def test_with_no_hosts(self):
        hosts = Hosts()
        assert hosts.next() is None

    def test_with_hosts(self):
        hostname_array = [
            "foo.example.com",
            "bar.example.com",
            "baz.example.com"
        ]
        hosts = Hosts(hostname_array)
        assert type(hosts.next()) is str
        assert type(hosts.next()) is str
        assert type(hosts.next()) is str
        assert type(hosts.next()) is str
        assert type(hosts.next()) is str

    def test_with_hosts_for_host_fixing(self):
        hostname_array = [
            "foo.example.com",
            "bar.example.com",
            "baz.example.com",
            "foo2.example.com",
            "bar2.example.com",
            "baz2.example.com"
        ]
        hosts = Hosts(hostname_array)

        # Make 6 selections from next()
        selected_hosts = []
        selected_hosts.append(hosts.next())
        selected_hosts.append(hosts.next())
        selected_hosts.append(hosts.next())
        selected_hosts.append(hosts.next())
        selected_hosts.append(hosts.next())
        selected_hosts.append(hosts.next())

        # check the len of a uniq'd selection to
        # make sure we're not stuck on the same host
        assert len(list(set(selected_hosts))) > 1
