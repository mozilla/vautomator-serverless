import logging

# This is an example of an on demand scan that an engineer might run should they have
# interest in getting immediate vulnerability data about a given FQDN. This would be
# the interface an engineer could use to kick off a VA.

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

fqdn = input("Provide the FQDN (Fully Qualified Domain Name) you want to scan: ")
# TODO: add relevant tasking call here to /ondemand/portscan
logger.info("Sends POST to https://<YOUR-API-ENDPOINT>/dev/ondemand/portscan")
logger.info("Triggered a Port Scan of: {}".format(fqdn))

# TODO: add relevant tasking call here to /ondemand/httpobservatory
logger.info("Sends POST to https://<YOUR-API-ENDPOINT>/dev/ondemand/httpobservatory")
logger.info("Triggered an HTTP Observatory Scan of: {}".format(fqdn))

# TODO: add relevant tasking call here to /ondemand/tlsobservatory
logger.info("Sends POST to https://<YOUR-API-ENDPOINT>/dev/ondemand/tlsobservatory")
logger.info("Triggered an SSH Observatory Scan of: {}".format(fqdn))

# TODO: add relevant tasking call here to /ondemand/sshobservatory
logger.info("Sends POST to https://<YOUR-API-ENDPOINT>/dev/ondemand/sshobservatory")
logger.info("Triggered an SSH Observatory Scan of: {}".format(fqdn))