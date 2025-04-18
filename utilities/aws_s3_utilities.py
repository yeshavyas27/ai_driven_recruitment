import os
from urllib.parse import urlparse

from constants.aws import AWSConstants


def s3_url_format(s3_key):
    s3_url = AWSConstants.S3_URL_FORMAT.format(
        bucket_name = os.getenv("AWS_S3_BUCKET"),
        region_name = os.getenv("AWS_DEFAULT_REGION"),
        key=s3_key
    )

    return s3_url

def get_s3_key_from_url(s3_url):
    # Extract the S3 key from the URL
    parsed_url = urlparse(s3_url)
    s3_key = os.path.basename(parsed_url.path)
    
    return s3_key
