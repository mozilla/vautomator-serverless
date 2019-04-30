import googlesearch
import requests
import os
import logging


class WebSearcher(object):
    def __init__(self, hostname, max_results=15, logger=logging.getLogger(__name__)):
        self.host = hostname
        self.max_results = max_results
        self.logger = logger

    def scan(self):
        # This is technically not a scan, however
        # keeping the name to be consistent
        # Search for security hits but without the host domain (ie "not their pages")
        search_results = []
        self.logger.info("[+] Running a web search on {}...".format(self.host))
        for m in googlesearch.search(
            query="{} security -site:{}".format(self.host, self.host), num=15
        ):
            search_results.append(m)
            if len(search_results) >= self.max_results:
                break

        if len(search_results) > 0:
            return search_results
        else:
            self.logger.error("[-] No results from web search for {}".format(self.host))
