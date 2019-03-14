import random
import requests
import os


class Hosts(object):
    """Return host(s) for scheduled scans."""

    def __init__(self, hosts=[]):
        self.hosts = hosts
        self.hostlistURL = os.getenv('HOST_LIST')

    def next(self):
        if len(self.hosts) > 0:
            return random.choice(self.hosts)

    def getList(self):
        if len(self.hosts) == 0:
            r = requests.get(self.hostlistURL).json()
            for category in r['sites']:
                for site in r['sites'][category]:
                    for hostname in r['sites'][category][site]:
                        self.hosts.append(hostname)
            return self.hosts
        return self.hosts
