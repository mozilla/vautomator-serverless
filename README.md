# vautomator-serverless
Repository to experiment with serverless framework and automation.

This project uses serverless framework and attempts to create a serverless environment that could be used to automate vulnerability assessment tasks with multiple ingestion points, such as on-demand submission of a host via a REST API, regular scanning of a list of hosts and proactive scanning of hosts appearing in Certificate Transparency logs.

This is under development with more features being added as different branches. `master` branch currently only supports:
- Scheduled HTTP Observatory scans (runs every 5 minutes)
- HTTP Observatory scan of a host manually submitted to an SQS queue
Ingestion points for both is a hard-coded list of hosts (for PoC purposes).

Results from the scheduled scans are placed in an S3 bucket specified in `serverless.yml`.

## Get ready to deploy

1. Install serverless framework: `npm install -g serverless`
2. Install `serverless-python-requirements` plugin for serverless: `npm install --save serverless-python-requirements`
3. Download the repo: `git clone https://github.com/mozilla/vautomator-serverless.git && cd vautomator-serverless`
4. Setup your AWS environment/profile. An account or role with at least the permissions listed in [serverless.yml](https://github.com/mozilla/vautomator-serverless/blob/master/serverless.yml#L10-L26) is required in order to deploy and run this.
5. Customise your `serverless.yml` file, in particular the `custom` section where you can specify your own S3 bucket name etc.
6. Once your AWS profile is set up, run: `serverless deploy -v`
7. If you have no CloudFormation errors and if you see `Service Information` listing your lambda functions/endpoints, you are good to go.

## Running

The current branch does not do much, however you can observe that scheduled scans are running by monitoring the CloudWatch logs with `serverless logs -f cronObservatoryScan -t`.

```
START RequestId: 6a3bc71b-e369-498c-849c-f522e79ce734 Version: $LATEST
2019-03-11 17:16:59.974 (+11:00)	6a3bc71b-e369-498c-849c-f522e79ce734	[INFO]	Tasking Observatory Scan of: "infosec.mozilla.org"
2019-03-11 17:17:00.439 (+11:00)	6a3bc71b-e369-498c-849c-f522e79ce734	[INFO]	Completed Observatory Scan of "infosec.mozilla.org"
```

To confirm the scan was performed and results were stored in S3:
```
$ aws s3 ls s3://<your-bucket-name>
2019-03-12 15:32:00       6906 infosec.mozilla.org.json
```
