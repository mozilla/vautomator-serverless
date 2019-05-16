import boto3
import json
import logging
import os

client = boto3.client('s3')
S3_BUCKET = os.environ.get('S3_BUCKET')


def send_to_s3(hostname, scan_json):
    key = "{}.{}".format(hostname, "json")

    client.put_object(Body=json.dumps(scan_json, indent=4, sort_keys=True), Bucket=S3_BUCKET,
                      Key=key, ACL='public-read')
    url = "https://s3.amazonaws.com/{}/{}".format(S3_BUCKET, key)
    logging.info("Uploaded result file to URL: {}".format(url))


def search_s3(hostname):
    scan_output_list = []
    for scan_result in client.list_objects(Bucket=S3_BUCKET, Prefix=hostname)['Contents']:
        scan_output_list.append(str(scan_result['Key']))

    return scan_output_list


def download_s3(scan_output_list, target_dir):
    for output in scan_output_list:
        client.download_file(
            S3_BUCKET,
            output,
            target_dir + '/{}'.format(output)
        )
