import logging
import sys
import datetime
import certstream
import json
import requests

# This is an example of a long-running service/process which will monitor for
# CT Logs in real-time and as soon as a certificat_update action is triggered
# for a domain pattern we care about, we will immediately take action to task
# port scans and observatory scans by calling our public REST API endpoints

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def print_callback(message, context):
    logging.debug("Message -> {}".format(message))

    if message['message_type'] == "certificate_update":
        all_domains = message['data']['leaf_cert']['all_domains']

        domain_patterns = [
            ".mozilla.com",
            ".mozilla.org",
            ".firefox.com",
        ]

        for fqdn in all_domains:
            for domain_pattern in domain_patterns:
                # We want all legit FDQNs, but we can't scan wild-cards
                if fqdn.endswith(domain_pattern) and ('*' not in fqdn):

                    # TODO: add relevant tasking call here to /ondemand/portscan
                    logger.info("Sends POST to https://<YOUR-API-ENDPOINT>/dev/ondemand/portscan")
                    logger.info("Triggered a Port Scan of: {}".format(fqdn))

                    # TODO: add relevant tasking call here to /ondemand/httpobservatory
                    logger.info("Sends POST to https://<YOUR-API-ENDPOINT>/dev/ondemand/httpobservatory")
                    logger.info("Triggered an HTTP Observatory Scan of: {}".format(fqdn))

                    # TODO: add relevant tasking call here to /ondemand/sshobservatory
                    logger.info("Sends POST to https://<YOUR-API-ENDPOINT>/dev/ondemand/sshobservatory")
                    logger.info("Triggered an SSH Observatory Scan of: {}".format(fqdn))

                    # TODO: add relevant tasking call here to /ondemand/tlsobservatory
                    logger.info("Sends POST to https://<YOUR-API-ENDPOINT>/dev/ondemand/tlsobservatory")
                    logger.info("Triggered an SSH Observatory Scan of: {}".format(fqdn))


logging.basicConfig(format='[%(levelname)s:%(name)s] %(asctime)s - %(message)s', level=logging.INFO)

certstream.listen_for_events(print_callback, url='wss://certstream.calidog.io/')
