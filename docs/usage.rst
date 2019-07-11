############
Usage
############

On-demand scans are performed by invoking a handful of REST APIs. At this time, the request 
and response formats for most of the APIs are very simple - they expect a host as input, and
return a UUID for the scan (if the host is valid). Valid host types are: FQDN, IPv4. 
The REST API supports JSON.

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
    a typical vulnerability assessment process for a given host. Below is the output from
    a sample run:

    .. parsed-literal::

       Provide the FQDN (Fully Qualified Domain Name) you want to scan: www.mozilla.org
       INFO:root:Sending POST to https://y2ippncfd1.execute-api.us-west-2.amazonaws.com/dev/ondemand/portscan
       INFO:root:Triggered a port scan of: www.mozilla.org
       INFO:root:Sending POST to https://y2ippncfd1.execute-api.us-west-2.amazonaws.com/dev/ondemand/httpobservatory
       INFO:root:Triggered a httpobservatory scan of: www.mozilla.org
       INFO:root:Sending POST to https://y2ippncfd1.execute-api.us-west-2.amazonaws.com/dev/ondemand/tlsobservatory
       INFO:root:Triggered a tlsobservatory scan of: www.mozilla.org
       INFO:root:Sending POST to https://y2ippncfd1.execute-api.us-west-2.amazonaws.com/dev/ondemand/sshobservatory
       INFO:root:Triggered a sshobservatory scan of: www.mozilla.org
       INFO:root:Sending POST to https://y2ippncfd1.execute-api.us-west-2.amazonaws.com/dev/ondemand/websearch
       INFO:root:Triggered a websearch scan of: www.mozilla.org
       INFO:root:Sending POST to https://y2ippncfd1.execute-api.us-west-2.amazonaws.com/dev/ondemand/tenablescan
       INFO:root:Triggered a tenable scan of: www.mozilla.org
       INFO:root:Sending POST to https://y2ippncfd1.execute-api.us-west-2.amazonaws.com/dev/ondemand/direnum
       INFO:root:Triggered a direnum scan of: www.mozilla.org
       INFO:root:Scans kicked off for www.mozilla.org. Run "download_results.py" in 15 minutes to have the scan results.

*   ``realtime_ctlog_tasker.py`` is a client which monitors/streams the Certificate
    Transparency logs for a hard-coded list of domains of interest. If a subdomain of these
    domains appear in the CT logs, the client sequentially invokes all API endpoints detailed
    below. Note that this is not an interactive client, by nature it works more like a daemon.
    Access to CT logs is provided by `certstream <https://github.com/CaliDog/certstream-python>`_.
*   ``download_results.py`` is an interactive client which takes a host as input and
    invokes the ``/results`` endpoint to download the scan results. Results are downloaded in
    compressed format. Below is the output from a sample run:

    .. parsed-literal::

       Provide the FQDN (Fully Qualified Domain Name) you want the results for: www.mozilla.org
       INFO:root:Sending POST to https://y2ippncfd1.execute-api.us-west-2.amazonaws.com/dev/results
       INFO:root:Downloaded scan results for: www.mozilla.org, saving to disk...
       INFO:root:Scan results for www.mozilla.org are saved in the results folder.

REST API
===========

POST /scan
------------
Perform all supported scans on a given host.

Parameters
+++++++++++
*   ``target`` is the host (FQDN or IPv4 address)
Output
+++++++
*   A ``json`` document containing step function execution name.

Example
++++++++
.. parsed-literal::
   curl -X POST 'https://y2ippncfd1.execute-api.us-west-2.amazonaws.com/dev/scan' \
   -d '{"target": "www.mozilla.org"}' -H 'X-Api-Key: abcdefgh12345678'

   {"executionArn":"<executionARN>:ScanAll:e9648493-9c01-11e9-85f4-874b479eba5f","startDate":1.561986763711E9}

.. note:: This is an asynchronous endpoint. Behind the scenes, the host is processed 
   by a state machine, which invokes a number of Lambda functions to perform all scans 
   on the host, and an email is sent to desired parties when all scans are completed 
   and results are available.

----

POST /ondemand/portscan
-------------------------
Add a target to the scan queue for port scan.

Parameters
+++++++++++
*   ``target`` is the host (FQDN or IPv4 address)
Output
+++++++
*   A ``json`` document containing a UUID associated with the scan.

Example
++++++++
.. parsed-literal::
   curl -X POST 'https://y2ippncfd1.execute-api.us-west-2.amazonaws.com/dev/ondemand/portscan' \
   -d '{"target": "www.mozilla.org"}' -H 'X-Api-Key: abcdefgh12345678'

   {"uuid": "ac90f64c-3516-4449-bf4e-040d2f18fdc9"}

----

POST /ondemand/httpobservatory
-------------------------------
Add a target to the scan queue for `HTTP Observatory <https://observatory.mozilla.org/>`_ scan.

Parameters
+++++++++++
*   ``target`` is the host (FQDN or IPv4 address)

.. note:: While this endpoint will accept an IPv4 address, HTTP Observatory will not run a
   scan for an IP address only. vautomator will not complain, rather the HTTP Observatory
   scan results for the target will be empty.
Output
+++++++
*   A ``json`` document containing a UUID associated with the scan.

Example
++++++++
.. parsed-literal::
   curl -X POST 'https://y2ippncfd1.execute-api.us-west-2.amazonaws.com/dev/ondemand/httpobservatory' \
   -d '{"target": "www.mozilla.org"}' -H 'X-Api-Key: abcdefgh12345678'

   {"uuid": "6dd38a01-4d2d-4781-8db1-3ab65b63e1fb"}

----

POST /ondemand/tlsobservatory
-------------------------------
Add a target to the scan queue for `TLS Observatory <https://github.com/mozilla/tls-observatory>`_ scan.

Parameters
+++++++++++
*   ``target`` is the host (FQDN or IPv4 address)

Output
+++++++
*   A ``json`` document containing a UUID associated with the scan.

Example
++++++++
.. parsed-literal::
   curl -X POST 'https://y2ippncfd1.execute-api.us-west-2.amazonaws.com/dev/ondemand/tlsobservatory' \
   -d '{"target": "www.mozilla.org"}' -H 'X-Api-Key: abcdefgh12345678'

   {"uuid": "31c1f82e-83e2-4ccf-b245-8907d0a9eee8"}

----

POST /ondemand/sshobservatory
-------------------------------
Add a target to the scan queue for `SSH Observatory <https://github.com/mozilla/ssh_scan_api>`_ scan.

Parameters
+++++++++++
*   ``target`` is the host (FQDN or IPv4 address)

Output
+++++++
*   A ``json`` document containing a UUID associated with the scan.

Example
++++++++
.. parsed-literal::
   curl -X POST 'https://y2ippncfd1.execute-api.us-west-2.amazonaws.com/dev/ondemand/sshobservatory' \
   -d '{"target": "www.mozilla.org"}' -H 'X-Api-Key: abcdefgh12345678'

   {"uuid": "be32e717-c72e-41d9-806f-fd4de805aae4"}

----

POST /ondemand/websearch
--------------------------
Add a target to the scan queue for a Google web search of a target with a keyword ``security``.

Parameters
+++++++++++
*   ``target`` is the host (FQDN or IPv4 address)

Output
+++++++
*   A ``json`` document containing a UUID associated with the scan.

Example
++++++++
.. parsed-literal::
   curl -X POST 'https://y2ippncfd1.execute-api.us-west-2.amazonaws.com/dev/ondemand/websearch' \
   -d '{"target": "www.mozilla.org"}' -H 'X-Api-Key: abcdefgh12345678'

   {"uuid": "0b9e2375-1e8a-4921-8bb4-1e82f695d1dc"}

----

POST /ondemand/direnum
--------------------------
Add a target to the scan queue for a directory enumeration scan.

Parameters
+++++++++++
*   ``target`` is the host (FQDN or IPv4 address)

Output
+++++++
*   A ``json`` document containing a UUID associated with the scan.

Example
++++++++
.. parsed-literal::
   curl -X POST 'https://y2ippncfd1.execute-api.us-west-2.amazonaws.com/dev/ondemand/direnum' \
   -d '{"target": "www.mozilla.org"}' -H 'X-Api-Key: abcdefgh12345678'

   {"uuid": "1c124924-2938-423b-a42a-489e2dc8ac64"}

----

POST /ondemand/tenablescan
---------------------------
Add a target to the scan queue for a `Tenable.io <https://cloud.tenable.com>`_ scan.

.. note:: This endpoint will accept submissions, however a Tenable scan will not run unless
   vautomator was deployed with Tenable.io support during 
   `setup <https://vautomator-serverless.rtfd.io/en/latest/setup.html>`_ (see step 7).

Parameters
+++++++++++
*   ``target`` is the host (FQDN or IPv4 address)

Output
+++++++
*   A ``json`` document containing a UUID associated with the scan.

Example
++++++++
.. parsed-literal::
   curl -X POST 'https://y2ippncfd1.execute-api.us-west-2.amazonaws.com/dev/ondemand/tenablescan' \
   -d '{"target": "www.mozilla.org"}' -H 'X-Api-Key: abcdefgh12345678'

   {"uuid": "a778ada0-051f-464f-bf18-599d051f0fac"}

----

POST /results
---------------
Downloads the scan results available for the requested host.

Parameters
+++++++++++
*   ``target`` is the host (FQDN or IPv4 address)

.. note:: In order for this endpoint to work properly, the request made must contain a
   ``'Accept: application/gzip'`` header (This is an AWS API gateway caveat).

Output
+++++++
*   A binary blob (``application/gzip``) containing compressed scan results for the host.

Example
++++++++
.. parsed-literal::
   curl -X POST 'https://y2ippncfd1.execute-api.us-west-2.amazonaws.com/dev/results' \
   -d '{"target": "www.mozilla.org"}' -H 'X-Api-Key: abcdefgh12345678' \
   -H 'Accept: application/gzip' > www.mozilla.org__results.tgz
