import sys
import pytest
import os
import json
import requests
from scanners.websearcher import WebSearcher
from lib.target import Target


class TestWebSearcher(object):
    def test_defaults(self):
        web_searcher = WebSearcher()
        assert web_searcher.max_results == 15

    def test_scan(self):
        # Stub env var for testing
        host_name = "www.mozilla.org"
        web_searcher = WebSearcher()
        search_results = web_searcher.search(host_name)

        # Check to see is some of the expected JSON elements
        # are in the result to ensure it's working
        assert 'host' in search_results
        assert 'search' in search_results
        assert len(search_results['search']) <= 15
        assert len(search_results['search']) > 0
