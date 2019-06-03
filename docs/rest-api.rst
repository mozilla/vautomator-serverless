############
REST API
############

The REST API currently supports:

*   Addition of a target to the scan queue for port scan by an API endpoint (/ondemand/portscan).
*   Addition of a target to the scan queue for HTTP Observatory scan by an API endpoint (/ondemand/httpobservatory)
*   Addition of a target to the scan queue for TLS Observatory scan by an API endpoint (/ondemand/tlsobservatory)
*   Addition of a target to the scan queue for SSH Observatory scan by an API endpoint (/ondemand/sshobservatory).
*   Addition of a target to the scan queue for a directory enumeration scan (currently with dirb) by an API endpoint (/ondemand/direnum)
*   Addition of a target to the scan quque for a Google web search by an API endpoint (/ondemand/websearch)
*   [OPTIONAL] Addition of a target to the scan queue for a Tenable.io scan by an API endpoint (/ondemand/tenablescan).
*   An endpoint to retrieve the scan results for a given host (/results)