import logging
import json


class Event():
    def __init__(self, event, context, logger=logging.getLogger(__name__)):
        self.event = event
        self.context = context
        self.type = "api-gw"
        self.logger = logger

    def parse(self):
        try:
            json.loads(self.event['body'])
        except KeyError as e:
            if len(self.event) == 1 or 'results' in self.event:
                # If we are here, the event source is a step function
                self.type = "step-function"
            else:
                self.logger.error("Cannot parse event: '{}, context: {}, exception: ".format(str(self.event), self.context.function_name, e))
                self.type = "invalid"
                return False
        except Exception as e:
            # Likely ValueError, or some other exception,
            # but we do not really care
            self.logger.error("Cannot parse event: '{}, context: {}, exception: {}".format(str(self.event), self.context.function_name, e))
            self.type = "invalid"
            return False

        # Regardless of the type, we expect the event to contain
        # the keyword "target", as this is the host submitted
        if "target" not in str(self.event):
            self.logger.error("Invalid event: {}".format(self.event))
            self.type = "invalid"
            return False

        if "step" in self.type:
            return self.event
        else:
            return json.loads(self.event['body'])
