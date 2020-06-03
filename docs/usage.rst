############
Usage
############

On-demand scans are performed by invoking a handful of REST APIs. At this time, the request and response formats for most of the APIs are very simple - they expect a host as input, and return a UUID for the scan (if the host is valid). Valid host types are: FQDN, IPv4. 

The REST API supports JSON.

The recommended method to use vautomator-serverless APIs in a vulnerability assessment is to use the `vautomator-client <https://github.com/mozilla/vautomator-client>`__.

You could use another tool such as ``curl`` to invoke them (see the REST API section below).

.. note:: At this time, all REST API endpoints are protected with an API key, which
   must be specified in an ``X-Api-Key HTTP`` header. If using the ``vautomator-client``, this key will be retrieved by the client, provided that you are using the same AWS profile/role used to deploy ``vautomator-serverless``. If not, the client will prompt you to enter an API key.

For a detailed usage of ``vautomator-client``, refer to: https://github.com/mozilla/vautomator-client/blob/master/README.md

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
   curl -X POST 'https://vautomator.security.allizom.org/scan' \
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
   curl -X POST 'https://vautomator.security.allizom.org/ondemand/portscan' \
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
   curl -X POST 'https://vautomator.security.allizom.org/ondemand/httpobservatory' \
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
   curl -X POST 'https://vautomator.security.allizom.org/ondemand/tlsobservatory' \
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
   curl -X POST 'https://vautomator.security.allizom.org/ondemand/sshobservatory' \
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
   curl -X POST 'https://vautomator.security.allizom.org/ondemand/websearch' \
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
   curl -X POST 'https://vautomator.security.allizom.org/ondemand/direnum' \
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
   curl -X POST 'https://vautomator.security.allizom.org/ondemand/tenablescan' \
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
   curl -X POST 'https://vautomator.security.allizom.org/results' \
   -d '{"target": "www.mozilla.org"}' -H 'X-Api-Key: abcdefgh12345678' \
   -H 'Accept: application/gzip' > www.mozilla.org__results.tgz
