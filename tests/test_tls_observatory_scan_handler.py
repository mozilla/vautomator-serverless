import sys
import pytest
import os
import json
from lib.tlsobsscan_handler import TLSObsScanHandler


class TestTLSObsScanHandler():
    def test_creation(self):
        tlsobs_scan_handler = TLSObsScanHandler()
        assert type(tlsobs_scan_handler) is TLSObsScanHandler

    def test_queue(self):
        test_event = {"body": '{"target": "ssh.mozilla.com"}'}
        test_context = None
        tlsobs_scan_handler = TLSObsScanHandler()
        response = tlsobs_scan_handler.queue(test_event, test_context)
        assert response.response_dict == {}