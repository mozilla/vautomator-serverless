import sys
import pytest
import os
import json
from lib.response import Response


class TestResponse():
    # Make sure we leave these headers alone
    def test_without_security_headers(self):
        original_response = {
            "statusCode": 200,
            "body": json.dumps({'foo': 'bar'})
        }

        response = Response(original_response)

        assert type(Response(original_response)) == Response
        assert response.without_security_headers() == {
            'body': '{"foo": "bar"}', 'statusCode': 200}

    # Make sure we add security header to these responses
    def test_with_security_headers(self):
        original_response = {
            "statusCode": 200,
            "body": json.dumps({'foo': 'bar'})
        }

        new_headers_expectation = Response.SECURITY_HEADERS

        response = Response(original_response)

        assert type(Response(original_response)) == Response
        assert response.with_security_headers() == {'body': '{"foo": "bar"}',
                                                    'headers': new_headers_expectation,
                                                    'statusCode': 200}

    # Make sure we respect existing non-sec headers and don't remove them
    def test_with_security_headers_and_preexisting_non_sec(self):
        original_headers = {
            'foo': 'bar'
        }

        original_response = {
            "statusCode": 200,
            "body": json.dumps({'foo': 'bar'}),
            # We're adding to make sure it's not overwritten
            'headers': original_headers
        }

        new_headers_expectation = {}
        new_headers_expectation.update(original_headers)
        new_headers_expectation.update(Response.SECURITY_HEADERS)

        response = Response(original_response)

        assert type(Response(original_response)) == Response
        assert response.with_security_headers() == {'body': '{"foo": "bar"}',
                                                    'headers': new_headers_expectation,
                                                    'statusCode': 200}

    # Make sure we respect existing sec headers and don't over-write them
    def test_with_security_headers_preexisting_sec(self):
        original_headers = {
            'Content-Security-Policy': 'nope'
        }

        original_response = {
            "statusCode": 200,
            "body": json.dumps({'foo': 'bar'}),
            # We're adding to make sure it's not overwritten
            'headers': original_headers
        }

        new_headers_expectation = {}
        new_headers_expectation.update(Response.SECURITY_HEADERS)
        new_headers_expectation['Content-Security-Policy'] = 'nope'

        response = Response(original_response)

        assert type(Response(original_response)) == Response
        assert response.with_security_headers() == {'body': '{"foo": "bar"}',
                                                    'headers': new_headers_expectation,
                                                    'statusCode': 200}
