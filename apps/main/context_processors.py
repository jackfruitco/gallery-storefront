import os


def main(request):
    return {"SITE_NAME": os.getenv("SITE_NAME", "Gallery Storefront")}
