############
REST API
############

On-demand scans are performed by invoking a handful of REST APIs. At this time, the request 
and response formats for most of the APIs are very simple - they expect a host as input, and
return a UUID for the scan (if the host is valid). Valid host types are: FQDN, IPv4.

The recommended method to use these APIs in a vulnerability assessment is to
use the example clients under the ``examples`` directory. These are very simple clients 
written in Python, and are provided as samples (feel free to write your own, or you could 
use another tool such as ``curl`` to invoke them).

.. note:: At this time, all REST API endpoints are protected with an API key, which
   must be specified in an ``X-Api-Key HTTP`` header. If you opt to use the sample clients,
   ensure to specify your AWS profile either in the code or as an environment variable
   (``AWS_PROFILE``), and the clients will retrieve the API key for you.

There are 3 clients:

*   ``ondemand_tasker.py`` is an interactive client which takes a host as input and 
    sequentially invokes all API endpoints detailed below. Basically this clients automates
    a typical vulnerability assessment process for a given host.
*   ``realtime_ctlog_tasker.py`` is a client which monitors/streams the Certificate
    Transparency logs for a hard-coded list of domains of interest. If a subdomain of these
    domains appear in the CT logs, the client sequentially invokes all API endpoints detailed
    below. Note that this is not an interactive client, by nature it works more like a daemon.
    Access to CT logs is provided by `certstream <https://github.com/CaliDog/certstream-python>`_.
*   ``download_results.py`` is an interactive client which takes a host as input and
    invokes the ``/results`` endpoint to download the scan results. Results are downloaded in
    compressed format.

POST /ondemand/portscan
-------------------------
Add a target to the scan queue for port scan.



The REST API currently supports:

*   Addition of a target to the scan queue for port scan by an API endpoint (/ondemand/portscan).
*   Addition of a target to the scan queue for HTTP Observatory scan by an API endpoint (/ondemand/httpobservatory)
*   Addition of a target to the scan queue for TLS Observatory scan by an API endpoint (/ondemand/tlsobservatory)
*   Addition of a target to the scan queue for SSH Observatory scan by an API endpoint (/ondemand/sshobservatory).
*   Addition of a target to the scan queue for a directory enumeration scan (currently with dirb) by an API endpoint (/ondemand/direnum)
*   Addition of a target to the scan quque for a Google web search by an API endpoint (/ondemand/websearch)
*   [OPTIONAL] Addition of a target to the scan queue for a Tenable.io scan by an API endpoint (/ondemand/tenablescan).
*   An endpoint to retrieve the scan results for a given host (/results)