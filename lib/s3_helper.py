import boto3
import json
import logging
import os
from botocore.exceptions import ClientError

# S3_CLIENT = boto3.client('s3', 'us-west-2')
S3_BUCKET = os.environ.get('S3_BUCKET')


def send_to_s3(hostname, blob, client=None, bucket=S3_BUCKET):
    print(bucket)
    print(client)
    if isinstance(blob, dict):
        key = "{}.{}".format(hostname, "json")
        body = json.dumps(blob, indent=4, sort_keys=True)
    else:
        key = "/results/{}.{}".format(hostname, "tgz")
        body = blob

    client.put_object(Body=body, Bucket=bucket,
                      Key=key, ACL='authenticated-read')
    url = "https://s3.amazonaws.com/{}/{}".format(bucket, key)
    logging.info("Uploaded result file to URL: {}".format(url))
    return key


def search_s3(hostname, client=None, bucket=S3_BUCKET):
    print(bucket)
    print(client)
    scan_output_list = []
    for scan_result in client.list_objects(Bucket=bucket, Prefix=hostname)['Contents']:
        scan_output_list.append(str(scan_result['Key']))

    return scan_output_list


def download_s3(scan_output, target_dir, client=None, bucket=S3_BUCKET):
    print(bucket)
    print(client)
    if isinstance(scan_output, list):
        for output in scan_output:
            client.download_file(
                bucket,
                output,
                target_dir + '/{}'.format(output)
            )
    else:
        client.download_file(
            bucket,
            scan_output,
            target_dir + '/{}'.format(scan_output)
        )


def create_presigned_url(object_name, client=None, bucket=S3_BUCKET, expiration=86400):
    # Generate a presigned URL for the S3 object
    # The URL will be valid for 24 hours
    try:
        response = client.generate_presigned_url('get_object',
                                                 Params={'Bucket': bucket,
                                                         'Key': object_name},
                                                 ExpiresIn=expiration)
    except ClientError as e:
        logging.error("Error occurred while generating pre-signed URL: {}".format(e))
        return None
    # The response contains the presigned URL
    return response
