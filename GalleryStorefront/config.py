# Used for all global constants
# Can be imported to any python module for use

import os
from dataclasses import dataclass


def configure_s3(**kwargs):
    """Returns S3 configuration for Cloudflare R2"""
    config = {
        "bucket_name": os.getenv("CLOUDFLARE_R2_BUCKET", ""),
        "default_acl": os.getenv("CLOUDFLARE_R2_ACL", "public-read"),
        "signature_version": os.getenv("CLOUDFLARE_R2_SIGNATURE", "s3v4"),
        "endpoint_url": os.getenv("CLOUDFLARE_R2_ENDPOINT", ""),
        "access_key": os.getenv("CLOUDFLARE_R2_ACCESS_KEY", ""),
        "secret_key": os.getenv("CLOUDFLARE_R2_SECRET_KEY", ""),
    }
    for key, value in kwargs.items():
        config[key] = value
    return config


@dataclass
class S3_Config:
    bucket_name: str = os.getenv("CLOUDFLARE_R2_BUCKET", None)
    default_acl: str = os.getenv("CLOUDFLARE_R2_ACL", "public-read")
    signature_version: str = os.getenv("CLOUDFLARE_R2_SIGNATURE", "s3v4")
    endpoint_url: str = os.getenv("CLOUDFLARE_R2_ENDPOINT", None)
    access_key: str = os.getenv("CLOUDFLARE_R2_ACCESS_KEY", None)
    secret_key: str = os.getenv("CLOUDFLARE_R2_SECRET_KEY", None)

    def __json__(self, **kwargs) -> dict:
        """
        Return JSON-serializable dict with configuration values for S3.

        :param kwargs: For additional S3 configuration options
        :return: JSON serializable dict
        """

        config = {
            self.bucket_name.__name__: self.bucket_name,
            self.default_acl.__name__: self.default_acl,
            self.signature_version.__name__: self.signature_version,
            self.endpoint_url.__name__: self.endpoint_url,
            self.access_key.__name__: self.access_key,
            self.secret_key.__name__: self.secret_key,
        }

        for key, value in kwargs.items():
            config[key] = value
        return config
