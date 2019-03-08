import random

# This assumes the format found in
# https://raw.githubusercontent.com/mozilla/http-observatory-dashboard/master/httpobsdashboard/conf/sites.json
# For instance:
#{
#  "sites": {
#    "category1": {
#      "site_name1": [
#        "hostname1"
#      ],
#      "site_name2": [
#        "hostname1",
#        "hostname2",
#      ],
#    },
#    "category2": {
#      "site_name1": [
#        "hostname1"
#      ],
#      "site_name2": [
#        "hostname1",
#        "hostname2",
#      ],
#    }
#}
#


class Randomizer(object):
    """Return a random hostname from sites.json."""

    def __init__(self, url_list=[]):
        self.url_list = url_list

    def next(self):
        return random.choice(self.url_list)