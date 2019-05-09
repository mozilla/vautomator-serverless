# vautomator-serverless
Repository to experiment with serverless framework and automation.

This project uses serverless framework and attempts to create a serverless environment that could be used to automate vulnerability assessment tasks from multiple ingestion points, such as on-demand submission of a host via a REST API, regular scanning of a known list of hosts, and opportunistically scanning of hosts appearing in Certificate Transparency logs.

This is under development with more features being added as different branches. The tool currently supports:
- Addition of a target to the scan queue for port scan by an API endpoint (`/ondemand/portscan`).
- Addition of a target to the scan queue for HTTP Observatory scan by an API endpoint (`/ondemand/httpobservatory`)
- Addition of a target to the scan queue for TLS Observatory scan by an API endpoint (`/ondemand/tlsobservatory`)
- Addition of a target to the scan queue for SSH Observatory scan by an API endpoint (`/ondemand/sshobservatory`).
- Addition of a target to the scan queue for a directory enumeration scan (currently with `dirb`) by an API endpoint (`/ondemand/direnum`)
- Addition of a target to the scan quque for a Google web search by an API endpoint (`/ondemand/websearch`)
- _[OPTIONAL]_ Addition of a target to the scan queue for a Tenable.io scan by an API endpoint (`/ondemand/tenablescan`).
- Performing requested scan type (port, HTTP Observatory, TLS Observatory or SSH Observatory) on hosts in the queue
- Scheduled port scans from a hard-coded list of hosts (disabled by default)
- Scheduled directory enumeration scans (via `dirb`) from a hard-coded list of hosts (disabled by default)
- Scheduled HTTP Observatory scans from a hard-coded list of hosts (for PoC purposes, runs once a day)
- Scheduled TLS Observatory scans from a hard-coded list of hosts (for PoC purposes, runs once a day)
- Scheduled SSH Observatory scans from a hard-coded list of hosts (for PoC purposes, runs once a day)
- Manually add a host to the scan queue (for PoC purposes).

All API endpoints are currently protected by an API key. This will be replaced with SSO integration.

Results from all scans are placed in an S3 bucket specified in `serverless.yml`.

Port scans are performed using a [statically compiled `nmap` binary](https://github.com/ernw/static-toolbox/releases/download/1.0.2/nmap-7.70SVN-b5bd185-x86_64-portable.zip), [packaged within the serverless application](https://github.com/mozilla/vautomator-serverless/blob/master/serverless.yml#L64-L66).

Directory enumeration scans are performed via `dirb`, compiled specifically for Amazon Linux and the binary and all supporting files packaged within the serverless application, similar to the `nmap` binary.

_**Note:** UDP port scans are not supported as Lamdba functions can not run as root/privileged users._

## Get ready to deploy

1. Install Python3 and [aws-cli](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-install.html).
2. Install serverless framework: `npm install -g serverless`
3. Download the repo: `git clone https://github.com/mozilla/vautomator-serverless.git && cd vautomator-serverless`
4. Customise your `serverless.yml` file, in particular the `custom` and `provider` sections where you can specify your own S3 bucket name/SQS name/KMS key (if using Tenable.io integration, see step 6) etc. or specify multiple environments, tag your resources etc.
5. Setup your AWS profile and credentials. An account or role with at least the permissions listed in [serverless.yml](https://github.com/mozilla/vautomator-serverless/blob/master/serverless.yml#L12-L36) is required in order to deploy and run this. _Currently we are using a role in the Mozilla Infosec Dev AWS account using role assumption._
6. Once your AWS profile is set up, modify the `Makefile` to specify your `AWS region` and `AWS profile`. Serverless framework supports role assumption, and so does the `Makefile`, as long as your AWS config and credentials files are setup as per [here](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-role.html).
7. [OPTIONAL] If you want Tenable.io integration via the `/ondemand/tenablescan` endpoint (otherwise skip to step 8):
    - Create a Tenable.io user account with _standard_ user permissions, and create an API key for this account.
    - Modify the top of the `Makefile` as follows:
        ```
        AWS_PROFILE := <YOUR-AWS-PROFILE/ROLE>
        # Y for Tenable.io support, N or blank if not
        TENABLE_IO := Y / N 
        
        # If you would like to create a dedicated KMS for vautomator,
        # specify a policy file here (an example policy file is
        # provided in the repository). Otherwise leave blank if
        # you would like to use default AWS SSM key for encrypted storage
        KMS_POLICY_FILE := <YOUR-KMS-POLICY-JSON-FILE>
        
        # Blank if a policy file is specified, 
        # or if you would like to use default AWS SSM key
        KMS_KEYID := <YOUR-KMS-KEY-ID> 
        ```

    - Once this is done, run `make setup TIOA=<Tenable-Access-Key> TIOS=<Tenable-Secret-Key>`. `TIOA` and `TIOS` are API keys generated in the first point above. Based on the above values in Makefile, this will create a new or use the default AWS KMS key, and store the Tenable API keys in SSM in encrypted form using the KMS key.
    _**NOTE**: The most straightforward option is to specify the AWS profile and `Y` for `TENABLE_IO`, and leave other variables blank._

8. [OPTIONAL] run: `make validate` to check if your `serverless.yml` is correctly formatted without deploying a stack.

9. Run `make deploy` to deploy to AWS!

10. If you have no CloudFormation errors and if you see `Service Information` listing your lambda functions/endpoints, you are good to go.

## Examples

- Once deployed properly, you can kick of an ondemand scan on a host, using: `API_PROFILE=<YOUR-AWS-PROFILE/ROLE> python3 examples/ondemand_tasker.py`. Alternatively, you can hard-code your AWS profile in a variable in the code for examples.
  
  Note: You must provide an AWS profile/role if you'd like to use them as clients. This is required in order to programmatically fetch the API gateway URL details for your vautomator-serverless instance, as well as the API gateway key which currently protects the REST APIs.

```
Provide the FQDN (Fully Qualified Domain Name) you want to scan: infosec.mozilla.org
INFO:root:Sending POST to <YOUR-REST-ENDPOINT>/ondemand/portscan
INFO:root:Triggered a port scan of: infosec.mozilla.org
INFO:root:Sending POST to <YOUR-REST-ENDPOINT>/ondemand/httpobservatory
INFO:root:Triggered a httpobservatory scan of: infosec.mozilla.org
INFO:root:Sending POST to <YOUR-REST-ENDPOINT>/ondemand/tlsobservatory
INFO:root:Triggered a tlsobservatory scan of: infosec.mozilla.org
INFO:root:Sending POST to <YOUR-REST-ENDPOINT>/ondemand/sshobservatory
INFO:root:Triggered an sshobservatory scan of: infosec.mozilla.org
INFO:root:Sending POST to <YOUR-REST-ENDPOINT>/ondemand/tenablescan
INFO:root:Triggered a tenable scan of: infosec.mozilla.org
INFO:root:Sending POST to <YOUR-REST-ENDPOINT>/ondemand/direnum
INFO:root:Triggered a direnum of: infosec.mozilla.org
INFO:root:Sending POST to <YOUR-REST-ENDPOINT>/ondemand/websearch
INFO:root:Triggered a web search of: infosec.mozilla.org
```

To confirm all scans were performed and results were stored in S3 bucket:

```
$ aws --profile <YOUR-PROFILE> s3 ls s3://<YOUR-S3-BUCKET> | sort -r | head -n 10
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
