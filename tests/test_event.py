import pytest
import os
import json
from lib.event import Event


class TestEvent():

    def test_defaults(self):
        test_event = Event()
        assert type(test_event) is Event
        assert test_event.event is None
        assert test_event.context is None
        assert test_event.type == "api-gw"

    def test_parse(self):
        target = "infosec.mozilla.org"
        partial_apigw_event = {"body": '{"target": "' + target + '"}'}
        partial_stepf_event = {"target": target}
        invalid_event = {"TEST": "TEST"}
        test_aws_context = None

        test_event_1 = Event(partial_apigw_event, test_aws_context)
        apigw_event = test_event_1.parse()
        assert test_event_1.type == "api-gw"
        assert apigw_event == partial_stepf_event

        test_event_2 = Event(partial_stepf_event, test_aws_context)
        step_function_event = test_event_2.parse()
        assert test_event_2.type == "step-function"
        assert partial_stepf_event == step_function_event

        test_event_3 = Event(invalid_event, test_aws_context)
        assert test_event_3.parse() is False
