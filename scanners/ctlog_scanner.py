import os
import certstream
import logging
import json

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class CTLogScanner():

    def __init__(self, poll_interval=1):
        self.ws_url = os.getenv('CERTSTREAM_WS_URL')

    def on_open(self, instance):
        logger.info("Connection to CT logs established.")

    def on_error(self, instance, exception):
        logger.error("Exception in CertStreamClient: " +
                     json.dumps(exception))

    def print_callback(self, message, context):

        if message['message_type'] == "certificate_update":
            all_domains = message['data']['leaf_cert']['all_domains']

            target_domains = [
                "mozilla.com",
                "mozilla.org",
                "firefox.com",
            ]

            for pattern in target_domains:
                if pattern in all_domains[1:]:
                    # add all_domains[0] to queue
                    print(all_domains[0])
            
            logger.info("Domains seen in stream: " 
                        + json.dumps(all_domains[1:]))
    
    def watchCTLogs(self):
        certstream.listen_for_events(self.print_callback,
                                     on_open=self.on_open,
                                     on_error=self.on_error,
                                     url=self.ws_url
                                     )
