import random


class Randomizer(object):
    """Return a random hostname from an array."""

    def __init__(self, hosts=[]):
        self.hosts = hosts

    def next(self):
        return random.choice(self.hosts)
