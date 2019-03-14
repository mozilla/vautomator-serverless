import socket
from netaddr import valid_ipv4
from urllib.parse import urlparse


class Target:

    def __new__(cls, *args, **kwargs):
        if cls._isValid(*args, **kwargs):
            instance = super(Target, cls).__new__(cls)
            return instance
    
    def __init__(self, name):
        self.targetname = name

    @classmethod
    def _isValid(cls, *args, **kwargs):
        # A target can be 2 things:
        # 1. FQDN
        # 2. IPv4 address

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
        try:
            # target name must not be empty
            assert kwargs['name']
            # target name must be a string
            assert isinstance(kwargs['name'], str)
            # target name must not start with anti-patterns
            for pattern in starts_with_anti_patterns:
                assert not kwargs['name'].startswith(pattern)
            # target name must be an FQDN or an IPv4 address
            assert cls._valid_fqdn(kwargs['name']) or \
                cls._valid_ip(kwargs['name'])
        except AssertionError:
            return False
        return True

    def _valid_ip(ip):
        if valid_ipv4(ip):
            return True
        return False

    def _valid_fqdn(hostname):
        try:
            socket.gethostbyname(hostname)
            return True
        except Exception:
            return False
