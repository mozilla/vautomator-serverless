# vautomator-serverless
Repository to experiment with serverless framework and automation.

This project uses serverless framework and attempts to create a serverless environment that could be used to automate vulnerability assessment tasks with multiple ingestion points, such as on-demand submission of a host via a REST API, regular scanning of a list of hosts and proactive scanning of hosts appearing in Certificate Transparency logs.

This is under development with more features being added as different branches. The current branch supports:
- Addition of a target to the scan queue for port scan by an API endpoint (`/ondemand/portscan`)
- Addition of a target to the scan queue for Observatory scan by an API endpoint (`/ondemand`)
- Performing requested scan type (port or Observatory) on hosts in the queue
- Daily scheduled port scans from a hard-coded list of hosts (for PoC purposes, currently disabled)
- Scheduled HTTP Observatory scans from a hard-coded list of hosts (for PoC purposes, runs every 5 minutes)
- Manually add a host to the queue (for PoC purposes).

Results from all scans are placed in an S3 bucket specified in `serverless.yml`.

Port scans are performed using a [statically compiled `nmap` binary](https://github.com/ernw/static-toolbox/releases/download/1.0.2/nmap-7.70SVN-b5bd185-x86_64-portable.zip), [packaged within the serverless application](https://github.com/mozilla/vautomator-serverless/blob/ondemand-port-scan/serverless.yml#L41-L43).

_**Note:** UDP port scans are not supported as Lamdba functions can not be as root/privileged users._

## Get ready to deploy

1. Install serverless framework: `npm install -g serverless`
2. Install `serverless-python-requirements` plugin for serverless: `npm install --save serverless-python-requirements`
3. Download the repo: `git clone -b ondemand-port-scan https://github.com/mozilla/vautomator-serverless.git && cd vautomator-serverless`
4. Setup your AWS environment/profile. An account or role with at least the permissions listed in [serverless.yml](https://github.com/mozilla/vautomator-serverless/blob/ondemand-port-scan/serverless.yml#L10-L33) is required in order to deploy and run this.
5. Customise your `serverless.yml` file, in particular the `custom` section where you can specify your own S3 bucket name/SQS name etc.
6. Once your AWS profile is set up, run: `serverless deploy -v`
7. If you have no CloudFormation errors and if you see `Service Information` listing your lambda functions/endpoints, you are good to go.

## Running

- Scheduled Observatory scans will run every 5 mins: `serverless logs -f cronObservatoryScan`

```
START RequestId: 6a3bc71b-e369-498c-849c-f522e79ce734 Version: $LATEST
2019-03-11 17:16:59.974 (+11:00)	6a3bc71b-e369-498c-849c-f522e79ce734	[INFO]	Tasking Observatory Scan of: "infosec.mozilla.org"
2019-03-11 17:17:00.439 (+11:00)	6a3bc71b-e369-498c-849c-f522e79ce734	[INFO]	Completed Observatory Scan of "infosec.mozilla.org"
```
- To kick off a port scan on a target on demand, do:
```
$ curl -X PUT -d '{"target": "www.smh.com.au"}' https://<YOUR-API-ENDPOINT>/dev/ondemand/portscan`
{"OK": "target added to the queue"}
```
  - Observe the target added to the scan queue with: `sls logs -f onDemandPortScan`

- To kick off an Observatory scan on a target on demand:
```
curl -X PUT -d '{"target": "www.smh.com.au"}' https://<YOUR-API-ENDPOINT>/dev/ondemand
{"OK": "target added to the queue"}
```
  - Observe the target added to the scan queue with: `sls logs -f onDemandObservatoryScan`

- Verify the queued scans actually run: `sls logs -f RunScanQueue`
```
START RequestId: 2298e8f2-17ac-5e78-8608-bdf388a42dba Version: $LATEST
END RequestId: 2298e8f2-17ac-5e78-8608-bdf388a42dba
REPORT RequestId: 2298e8f2-17ac-5e78-8608-bdf388a42dba	Duration: 590.75 ms	Billed Duration: 600 ms 	Memory Size: 1024 MB	Max Memory Used: 86 MB
```

To confirm all scans were performed and results were stored in S3:
```
$ aws s3 ls s3://<your-bucket-name>
2019-03-12 15:32:00       6906 infosec.mozilla.org.json
2019-03-12 22:52:00       6906 infosec.mozilla.org_observatory.json
2019-03-12 15:42:00       9209 www.mozilla.org.json
2019-03-12 22:27:00       9209 www.mozilla.org_observatory.json
2019-03-07 16:41:27       5630 www.smh.com.au_tcpscan.json
2019-03-12 22:49:33       5697 www.smh.com.au_observatory.json

```
