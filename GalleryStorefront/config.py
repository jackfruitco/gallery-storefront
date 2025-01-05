# Used for all global constants
# Can be imported to any python module for use

import os

STOREFRONT_URL = os.getenv('STOREFRONT_URL', '')

def configure_s3(**kwargs):
    """Returns S3 configuration for Cloudflare R2"""
    config = {
        "bucket_name": os.getenv('CLOUDFLARE_R2_BUCKET', ''),
        "default_acl": os.getenv('CLOUDFLARE_R2_ACL', 'public-read'),
        "signature_version": os.getenv('CLOUDFLARE_R2_SIGNATURE', 's3v4'),
        "endpoint_url": os.getenv('CLOUDFLARE_R2_ENDPOINT', ''),
        "access_key": os.getenv('CLOUDFLARE_R2_ACCESS_KEY', ''),
        "secret_key": os.getenv('CLOUDFLARE_R2_SECRET_KEY', ''),
    }
    for key, value in kwargs.items():
        config[key] = value
    return config