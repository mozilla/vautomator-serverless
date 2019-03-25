import sys
import pytest
import os
import json
from lib.portscan_handler import PortScanHandler


class TestPortScanHandler():
    def test_creation(self):
        port_scan_handler = PortScanHandler()
        assert type(port_scan_handler) is PortScanHandler

    def test_queue(self):
        test_event = {"body": '{"target": "ssh.mozilla.com"}'}
        test_context = None
        port_scan_handler = PortScanHandler()
        response = port_scan_handler.queue(test_event, test_context)
        assert response.response_dict == {}
