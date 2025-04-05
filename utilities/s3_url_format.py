import os

from constants.aws import AWSConstants

def s3_url_format(s3_key):
    s3_url = AWSConstants.S3_URL_FORMAT.format(
        bucket_name = os.getenv("AWS_S3_BUCKET"),
        region_name = os.getenv("AWS_DEFAULT_REGION"),
        key=s3_key
    )

    return s3_url
