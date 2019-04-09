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

## Examples

- Once deployed properly, you can kick of an ondemand scan on a host, using: `API_GW_URL=<YOUR-REST-ENDPOINT> python3 examples/ondemand_tasker.py`

```
Provide the FQDN (Fully Qualified Domain Name) you want to scan: infosec.mozilla.org
INFO:root:Sending POST to <YOUR-REST-ENDPOINT>
INFO:root:Triggered a Port Scan of: infosec.mozilla.org
INFO:root:Sending POST to <YOUR-REST-ENDPOINT>
INFO:root:Triggered an HTTP Observatory Scan of: infosec.mozilla.org
INFO:root:Sending POST to <YOUR-REST-ENDPOINT>
INFO:root:Triggered a TLS Observatory Scan of: infosec.mozilla.org
INFO:root:Sending POST to <YOUR-REST-ENDPOINT>
INFO:root:Triggered an SSH Observatory Scan of: infosec.mozilla.org
```

To confirm all scans were performed and results were stored in S3 bucket:

```
$ aws --profile <YOUR-PROFILE> s3 ls s3://<YOUR-S3-BUCKET> | sort -r
2019-04-10 00:03:17      10487 infosec.mozilla.org_httpobservatory.json
2019-04-10 00:03:22      77028 infosec.mozilla.org_tlsobservatory.json
2019-04-10 00:03:37       5709 infosec.mozilla.org_tcpscan.json
...
```

- Scheduled Observatory scans will run once a day: `serverless logs -f cronHttpObservatoryScan`

```
START RequestId: 6a3bc71b-e369-498c-849c-f522e79ce734 Version: $LATEST
2019-03-11 17:16:59.974 (+11:00)	6a3bc71b-e369-498c-849c-f522e79ce734	[INFO]	Tasking Observatory Scan of: "infosec.mozilla.org"
2019-03-11 17:17:00.439 (+11:00)	6a3bc71b-e369-498c-849c-f522e79ce734	[INFO]	Completed Observatory Scan of "infosec.mozilla.org"
```

- Verify the queued scans actually run: `sls logs -f RunScanQueue`
```
START RequestId: 2298e8f2-17ac-5e78-8608-bdf388a42dba Version: $LATEST
END RequestId: 2298e8f2-17ac-5e78-8608-bdf388a42dba
REPORT RequestId: 2298e8f2-17ac-5e78-8608-bdf388a42dba	Duration: 590.75 ms	Billed Duration: 600 ms 	Memory Size: 1024 MB	Max Memory Used: 86 MB
```
