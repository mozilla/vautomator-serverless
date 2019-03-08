import boto3
import json
import os
import logging

client = boto3.client('s3')


def send_to_s3(hostname, scan_json):
    key = "{}.{}".format(hostname, "json")
    bucket = "vautomator-results"

    client.put_object(Body=json.dumps(scan_json), Bucket=bucket,
                      Key=key, ACL='public-read')
    url = "https://s3.amazonaws.com/{}/{}".format(bucket, key)
    logging.info("Uploaded result file to URL: {}".format(url))
