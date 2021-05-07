"""
Load data from a local file

Adapted codes from: https://github.com/MSIA/2021-msia423/blob/main/aws-s3/s3.py
"""
import argparse
import logging
import re

import boto3
import botocore

logging.basicConfig(format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s', level=logging.DEBUG)
logging.getLogger("botocore").setLevel(logging.ERROR)
logging.getLogger("s3transfer").setLevel(logging.ERROR)
logging.getLogger("urllib3").setLevel(logging.ERROR)
logging.getLogger("boto3").setLevel(logging.ERROR)
logging.getLogger("asyncio").setLevel(logging.ERROR)
logging.getLogger("aiobotocore").setLevel(logging.ERROR)
logging.getLogger("s3fs").setLevel(logging.ERROR)


logger = logging.getLogger('s3')


def parse_s3(s3path):
    """
    parse the S3 path to return bucket name and the S3 path
    Args:
        s3path (str): full S3 path as input
    Returns:
        s3bucket (str): S3 bucket name
        s3path (str): S3 path
    """
    regex = r"s3://([\w._-]+)/([\w./_-]+)"

    m = re.match(regex, s3path)
    s3bucket = m.group(1)
    s3path = m.group(2)

    return s3bucket, s3path


def upload_file_to_s3(local_path, s3path):
    """
    Upload the file from the local path to s3
    Args:
        local_path (str): the path to the local data
        s3path (str): the s3 path that the data will be uploaded to
    Returns:
        None
    """
    s3bucket, s3_just_path = parse_s3(s3path)

    s3 = boto3.resource("s3")
    bucket = s3.Bucket(s3bucket)

    try:
        bucket.upload_file(local_path, s3_just_path)
    except botocore.exceptions.NoCredentialsError:
        logger.error('Please provide AWS credentials via AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY env variables.')
    else:
        logger.info('Data uploaded from %s to %s', local_path, s3path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--s3path', default='s3://2021-msia423-shen-binqi/raw/application_data.csv',
                        help="S3 data path to the data")
    parser.add_argument('--local_path', default='data/sample/application_data.csv',
                        help="local path to the data")
    args = parser.parse_args()

    upload_file_to_s3(args.local_path, args.s3path)
