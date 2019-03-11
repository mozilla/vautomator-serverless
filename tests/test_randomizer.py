import sys
import pytest
import os
import json
from util.randomizer import Randomizer


class TestRandomizer():
    def test_with_no_hosts(self):
        randomizer = Randomizer()
        with pytest.raises(IndexError):
            randomizer.next() == None

    def test_with_hosts(self):
        hosts = [
            "foo.example.com",
            "bar.example.com",
            "baz.example.com"
        ]
        randomizer = Randomizer(hosts)
        assert type(randomizer.next()) is str

    def test_with_hosts_for_host_fixing(self):
        hosts = [
            "foo.example.com",
            "bar.example.com",
            "baz.example.com",
            "foo2.example.com",
            "bar2.example.com",
            "baz2.example.com"
        ]
        randomizer = Randomizer(hosts)

        # Make 6 selections from next()
        selected_hosts = []
        selected_hosts.append(randomizer.next())
        selected_hosts.append(randomizer.next())
        selected_hosts.append(randomizer.next())
        selected_hosts.append(randomizer.next())
        selected_hosts.append(randomizer.next())
        selected_hosts.append(randomizer.next())

        # check the len of a uniq'd selection to
        # make sure we're not stuck on the same host
        assert len(list(set(selected_hosts))) > 1
