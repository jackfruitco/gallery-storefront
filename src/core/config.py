# Used for all global constants
# Can be imported to any python module for use
import os


class S3:
    BUCKET_NAME = os.getenv("CLOUDFLARE_R2_BUCKET", "")
    DEFAULT_ACL = os.getenv("CLOUDFLARE_R2_ACL", "public-read")
    SIGNATURE_VERSION = os.getenv("CLOUDFLARE_R2_SIGNATURE", "s3v4")
    ENDPOINT_URL = os.getenv("CLOUDFLARE_R2_ENDPOINT", "")
    ACCESS_KEY = os.getenv("CLOUDFLARE_R2_ACCESS_KEY", "")
    SECRET_KEY = os.getenv("CLOUDFLARE_R2_SECRET_KEY", "")

    @classmethod
    def get_config(cls, **kwargs):
        """Returns S3 configuration for Cloudflare R2"""

        config = {
            "bucket_name": cls.BUCKET_NAME,
            "default_acl": cls.DEFAULT_ACL,
            "signature_version": cls.SIGNATURE_VERSION,
            "endpoint_url": cls.ENDPOINT_URL,
            "access_key": cls.ACCESS_KEY,
            "secret_key": cls.SECRET_KEY,
        }

        for key, value in kwargs.items():
            config[key] = value
        return config
