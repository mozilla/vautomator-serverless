import googlesearch
import requests
import os
import logging


class WebSearcher(object):
    def __init__(self, max_results=15, logger=logging.getLogger(__name__)):
        self.max_results = max_results
        self.logger = logger

    def search(self, hostname):
        # Search for security hits but without the host domain (ie "not their pages")
        results = {}
        search_results = []
        results['search'] = search_results
        results['host'] = hostname

        self.logger.info("[+] Running a web search on {}...".format(hostname))
        for m in googlesearch.search(
            query="{} security -site:{}".format(hostname, hostname), num=15
        ):
            results['search'].append(m)
            if len(results['search']) >= self.max_results:
                break

        if len(results['search']) > 0:
            return results
        else:
            self.logger.error("[-] No results from web search for {}".format(hostname))
