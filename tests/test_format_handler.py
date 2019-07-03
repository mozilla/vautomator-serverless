import pytest
import os
from lib.format_handler import FormatHandler


class TestFormatHandler():

    def test_defaults(self):
        format_handler = FormatHandler()
        assert type(format_handler) is FormatHandler
        assert format_handler.default_format == "email"

    def test_formatForSNS(self):
        target = "infosec.mozilla.org"
        output_mapping = {
            'tcpscan': True,
            'tenablescan': True,
            'direnum': True,
            'sshobservatory': True,
            'httpobservatory': True,
            'tlsobservatory': True,
            'websearch': True
        }
        partial_stepf_event = {
            "target": target,
            "responses": {
                "Generatedownloadlink": {
                    "status": 200,
                    "output": output_mapping,
                    "url": "https://test-bucket.s3.amazonaws.com/"
                }
            }
        }
        test_context = None
        format_handler = FormatHandler()
        response = format_handler.formatForSNS(partial_stepf_event, test_context)

        assert 'subject' in response.keys()
        assert 'body' in response.keys()
        assert target in response['subject']

        invalid_event = {"TEST": "TEST"}
        response = format_handler.formatForSNS(invalid_event, test_context)

        assert response is False
