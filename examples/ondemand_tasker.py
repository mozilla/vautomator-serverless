import logging
import sys
import datetime
import json

# This is an example of an on demand scan that an engineer might run should they have
# interest in getting immediate vulnerability data about a given FQDN.  This would be
# the interface an engineer could use to kick off a VA.

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

fqdn = input("Provide the FQDN (Fully Qualified Domain Name) you want to scan: ")
# TODO: add relevant tasking call here to /ondemand/portscan, /ondemand/observatory, etc.
logger.info("Triggered a vulnerability scan of: {}".format(fqdn))
