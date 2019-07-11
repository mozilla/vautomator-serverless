import pytest
import os
from lib.formatter import Formatter


class TestFormatter():

    def test_defaults(self):
        formatter = Formatter()
        assert type(formatter) is Formatter
        assert formatter.default_format == "email"

    def test_formatForEmail_true(self):
        hostname = "infosec.mozilla.org"
        output_mapping = {
            'tcpscan': True,
            'tenablescan': True,
            'direnum': True,
            'sshobservatory': True,
            'httpobservatory': True,
            'tlsobservatory': True,
            'websearch': True
        }
        url = "https://test-bucket.s3.amazonaws.com/"
        formatter = Formatter()
        test_subject, test_body = formatter.formatForEmail((hostname, output_mapping, url))

        assert hostname in test_subject
        assert '\n' in test_body
        assert "successful" in test_body.lower()
        assert "unsuccessful" not in test_body.lower()
        assert url in test_body.lower()

    def test_formatForEmail_false(self):
        hostname = "infosec.mozilla.org"
        output_mapping = {
            'tcpscan': False,
            'tenablescan': False,
            'direnum': False,
            'sshobservatory': False,
            'httpobservatory': False,
            'tlsobservatory': False,
            'websearch': False
        }
        url = "https://test-bucket.s3.amazonaws.com/"
        formatter = Formatter()
        test_subject, test_body = formatter.formatForEmail((hostname, output_mapping, url))

        assert hostname in test_subject
        assert '\n' in test_body
        assert "unsuccessful" in test_body.lower()
        assert "manually" in test_body.lower()
        assert url in test_body.lower()
