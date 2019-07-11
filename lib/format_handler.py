import logging
import json
import os
import time
from lib.target import Target
from lib.event import Event
from lib.formatter import Formatter


class FormatHandler(object):

    def __init__(self, logger=logging.getLogger(__name__)):
        self.logger = logger
        self.default_format = "email"

    def formatForSNS(self, event, context):
        # This is a step function called from a state machine
        # Event type will always be "step-function"
        source_event = Event(event, context)
        data = source_event.parse()

        if data:
            target = Target(data.get('target'))
            if not target:
                self.logger.error("Target validation failed of: {}".format(target.name))
                return False

            # Extract the dictionary here and signed URL
            output_tracker = event['responses']['Generatedownloadlink']['output']
            signed_url = event['responses']['Generatedownloadlink']['url']
            contents = (target.name , output_tracker, signed_url)
            formatter = Formatter(self.logger)
            subject, body = formatter.formatForEmail(contents)

            return {
                'subject': subject,
                'body': body
            }

        else:
            self.logger.error("Unrecognized payload: {}".format(data))
            return False
