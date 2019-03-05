import random
import requests

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

    def __init__(self, url):
        self.url = url

    def next(self):
        r = requests.get(self.url).json()
        full_list_of_sites = []
        for category in r['sites']:
            for site in r['sites'][category]:
                for hostname in r['sites'][category][site]:
                    full_list_of_sites.append(hostname)
        return random.choice(full_list_of_sites)