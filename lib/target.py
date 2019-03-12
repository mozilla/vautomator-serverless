import socket
from netaddr import valid_ipv4
from urllib.parse import urlparse


class Target:

    # Here, tasklist is a list of Task objects
    def __init__(self, target, results_dict={}):
        self.targetname = target
        self.type = ""
        self.tasklist = []
        self.resultsdict = results_dict

    def isValid(self):
        # A target can be 2 things:
        # 1. FQDN
        # 2. IPv4 address

        if not isinstance(self.targetname, str):
            return False

        starts_with_anti_patterns = [
            "127.0.0", 
            "10.", 
            "172.",
            "192.168",
            "169.254.169.254",
            "http://",
            "ftp://",
            "ssh://"
            ]

        for pattern in starts_with_anti_patterns:
            if self.targetname.startswith(pattern):
                return False

        if self.valid_ip():
            self.type = "IPv4"
            self.targetdomain = self.targetname
            return True
        elif self.valid_fqdn():
            self.type = "FQDN"
            self.targetdomain = self.targetname
            return True
        else:
            return False

    def valid_ip(self):
        if valid_ipv4(self.targetname):
            self.type = "IPv4"
            return True
        return False

    def valid_fqdn(self):
        try:
            socket.gethostbyname(self.targetname)
            self.type = "FQDN"
            return True
        except Exception:
            return False
