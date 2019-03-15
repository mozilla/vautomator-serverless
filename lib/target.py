import socket
from netaddr import valid_ipv4
from urllib.parse import urlparse


class Target:
    def __init__(self, target_string):
        assert self._valid_class(target_string) == True
        assert self._valid_pattern(target_string) == True
        assert (self._valid_ip(target_string) == True or self._valid_fqdn(target_string) == True)
        self.name = target_string

    @classmethod
    def _valid_class(self, unknown_object):
        # It must be a str
        if isinstance(unknown_object, str):
            return True

        # It must be a valid class
        return False

    def _valid_pattern(self, unknown_string):
        # It must not be empty
        if not unknown_string:
            return False

        # It must not start with the following anti-patterns
        starts_with_anti_patterns = [
            "127.0.0",
            "10.",
            "172.",
            "192.168",
            "169.254.169.254",
            "http://",
            "ftp://",
            "ssh://",
        ]
        for pattern in starts_with_anti_patterns:
            if unknown_string.startswith(pattern):
                return False

        # It must be a valid pattern
        return True

    def _valid_ip(self, unknown_string):
        if valid_ipv4(unknown_string):
            return True
        return False

    def _valid_fqdn(self, unknown_string):
        try:
            socket.gethostbyname(unknown_string)
            return True
        except Exception:
            return False
