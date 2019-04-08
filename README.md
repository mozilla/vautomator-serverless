# vautomator-serverless
Repository to experiment with serverless framework and automation.

This project uses serverless framework and attempts to create a serverless environment that could be used to automate vulnerability assessment tasks from multiple ingestion points, such as on-demand submission of a host via a REST API, regular scanning of a known list of hosts, and opportunistically scanning of hosts appearing in Certificate Transparency logs.

This is under development with more features being added as different branches. The master branch supports:
- Addition of a target to the scan queue for port scan by an API endpoint (`/ondemand/portscan`). Due to the intrusive nature of this endpoint, it is protected by an API key.
- Addition of a target to the scan queue for HTTP Observatory scan by an API endpoint (`/ondemand/httpobservatory`)
- Addition of a target to the scan queue for TLS Observatory scan by an API endpoint (`/ondemand/tlsobservatory`)
- Addition of a target to the scan queue for SSH Observatory scan by an API endpoint (`/ondemand/sshobservatory`). This endpoint is protected by an API key.
- Performing requested scan type (port, HTTP Observatory, TLS Observatory or SSH Observatory) on hosts in the queue
- Scheduled port scans from a hard-coded list of hosts (disabled by default)
- Scheduled HTTP Observatory scans from a hard-coded list of hosts (for PoC purposes, runs once a day)
- Scheduled TLS Observatory scans from a hard-coded list of hosts (for PoC purposes, runs once a day)
- Scheduled SSH Observatory scans from a hard-coded list of hosts (for PoC purposes, runs once a day)
- Manually add a host to the scan queue (for PoC purposes).

Results from all scans are placed in an S3 bucket specified in `serverless.yml`.

Port scans are performed using a [statically compiled `nmap` binary](https://github.com/ernw/static-toolbox/releases/download/1.0.2/nmap-7.70SVN-b5bd185-x86_64-portable.zip), [packaged within the serverless application](https://github.com/mozilla/vautomator-serverless/blob/master/serverless.yml#L51-L53).

_**Note:** UDP port scans are not supported as Lamdba functions can not be as root/privileged users._

## Get ready to deploy

1. Install serverless framework: `npm install -g serverless`
2. Download the repo: `git clone https://github.com/mozilla/vautomator-serverless.git && cd vautomator-serverless`
3. Customise your `serverless.yml` file, in particular the `custom` and `provider` sections where you can specify your own S3 bucket name/SQS name etc. or specify multiple environments, tag your resources etc.
4. Setup your AWS profile and credentials. An account or role with at least the permissions listed in [serverless.yml](https://github.com/mozilla/vautomator-serverless/blob/master/serverless.yml#L12-L36) is required in order to deploy and run this. _Currently we are using a role in the Mozilla Infosec Dev AWS account using role assumption._
5. Once your AWS profile is set up, modify the `Makefile` to specify your `AWS region` and `AWS profile`. Serverless framework supports role assumption, and so does the `Makefile`, as long as your AWS config and credentials files are setup as per [here](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-role.html).
6. [OPTIONAL] run: `make validate` to check if your `serverless.yml` is correctly formatted without deploying a stack.
7. Run `make deploy` to deploy to AWS!
7. If you have no CloudFormation errors and if you see `Service Information` listing your lambda functions/endpoints, you are good to go.

## Running

- Scheduled Observatory scans will run once a day: `serverless logs -f cronHttpObservatoryScan`

```
START RequestId: 6a3bc71b-e369-498c-849c-f522e79ce734 Version: $LATEST
2019-03-11 17:16:59.974 (+11:00)	6a3bc71b-e369-498c-849c-f522e79ce734	[INFO]	Tasking Observatory Scan of: "infosec.mozilla.org"
2019-03-11 17:17:00.439 (+11:00)	6a3bc71b-e369-498c-849c-f522e79ce734	[INFO]	Completed Observatory Scan of "infosec.mozilla.org"
```
- To kick off a port scan on a target on demand, do:
```
$ curl --header "x-api-key: <API-KEY> -X POST -d '{"target": "www.smh.com.au"}' https://<YOUR-API-ENDPOINT>/dev/ondemand/portscan`
{"uuid": "3c74a069-4aac-4b3a-9f0e-29af42874b1b"}
```
  - Observe the target added to the scan queue with: `sls logs -f onDemandPortScan`

- To kick off an HTTP Observatory scan on a target on demand:
```
curl -X POST -d '{"target": "www.smh.com.au"}' https://<YOUR-API-ENDPOINT>/dev/ondemand/httpobservatory
{"uuid": "a542444e-8df3-47b5-a2b8-3e1b0f3c6668"}
```
  - Observe the target added to the scan queue with: `sls logs -f onDemandHttpObservatoryScan`

- To kick off an SSH Observatory scan on a target on demand:
```
curl -X POST -d '{"target": "www.mozilla.org"}' https://<YOUR-API-ENDPOINT>/dev/ondemand/sshobservatory
{"uuid": "a542444e-8df3-47b5-a2b8-3e1b0f3c6668"}
```
  - Observe the target added to the scan queue with: `sls logs -f onDemandSshObservatoryScan`

- To kick off a TLS Observatory scan on a target on demand:
```
curl -X POST -d '{"target": "www.mozilla.org"}' https://<YOUR-API-ENDPOINT>/dev/ondemand/tlsobservatory
{"uuid": "a542444e-8df3-47b5-a2b8-3e1b0f3c6668"}
```
  - Observe the target added to the scan queue with: `sls logs -f onDemandTlsObservatoryScan`

- Verify the queued scans actually run: `sls logs -f RunScanQueue`
```
START RequestId: 2298e8f2-17ac-5e78-8608-bdf388a42dba Version: $LATEST
END RequestId: 2298e8f2-17ac-5e78-8608-bdf388a42dba
REPORT RequestId: 2298e8f2-17ac-5e78-8608-bdf388a42dba	Duration: 590.75 ms	Billed Duration: 600 ms 	Memory Size: 1024 MB	Max Memory Used: 86 MB
```

To confirm all scans were performed and results were stored in S3:
```
$ aws s3 ls s3://<your-bucket-name>
2019-03-12 15:32:00       6906 infosec.mozilla.org_tcpscan.json
2019-03-12 22:52:00       6906 infosec.mozilla.org_httpobservatory.json
2019-03-12 22:52:00       6906 infosec.mozilla.org_sshobservatory.json
2019-03-12 15:42:00       9209 www.mozilla.org_tcpscan.json
2019-03-12 22:27:00       9209 www.mozilla.org_httpobservatory.json
2019-03-12 22:27:00       9209 www.mozilla.org_sshobservatory.json
2019-03-07 16:41:27       5630 www.smh.com.au_tcpscan.json
2019-03-12 22:49:33       5697 www.smh.com.au_httpobservatory.json
2019-03-12 22:49:33       5697 www.smh.com.au_sshobservatory.json
2019-03-17 20:42:54       5697 www.mozilla.org_tlsobservatory.json
```