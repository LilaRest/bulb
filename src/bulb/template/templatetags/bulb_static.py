from bulb.utils.log import bulb_logger
from urllib.parse import quote, urljoin
from django import template
from django.conf import settings
import os

register = template.Library()

BASE_DIR = os.environ["BASE_DIR"]


class BULBStaticTemplateTagsError(Exception):
    pass


@register.simple_tag()
def static_raw_src(path):
# def static_src(path):
    if settings.DEBUG:
        return urljoin(settings.STATIC_URL, quote(path))

    else:
        pull_url = settings.BULB_SFTP_PULL_URL

        if pull_url is not None:
            src_url = pull_url + "/staticfiles/raw_src/"
            return urljoin(src_url, quote(path))

        else:
            bulb_logger.error(
                'BULBStaticTemplateTagsError("To use the \'{% static_raw_src %}\' tag you must define the BULB_SFTP_PULL_URL variable in your \'settings.py\' file.")')
            raise BULBStaticTemplateTagsError(
                "To use the '{% static_raw_src %}' tag you must define the BULB_SFTP_PULL_URL variable in your 'settings.py' file.")


@register.simple_tag()
def static_bundled_src(path):
    if settings.DEBUG:
        return urljoin(os.path.join(BASE_DIR, "bundled_staticfiles"), quote(path))

    else:
        pull_url = settings.BULB_SFTP_PULL_URL

        if pull_url is not None:
            src_url = pull_url + "/staticfiles/bundled_src/"
            return urljoin(src_url, quote(path))

        else:
            bulb_logger.error(
                'BULBStaticTemplateTagsError("To use the \'{% static_bundle_src %}\' tag you must define the BULB_SFTP_PULL_URL variable in your \'settings.py\' file.")')
            raise BULBStaticTemplateTagsError(
                "To use the '{% static_bundle_src %}' tag you must define the BULB_SFTP_PULL_URL variable in your 'settings.py' file.")

@register.simple_tag()
def static_content(path):
    if settings.DEBUG or not settings.BULB_USE_SFTP:
        return urljoin(settings.STATIC_URL, quote(path))

    else:
        pull_url = settings.BULB_SFTP_PULL_URL

        if pull_url is not None:
            src_url = pull_url + "/staticfiles/content/"
            return urljoin(src_url, quote(path))

        else:
            bulb_logger.error(
                'BULBStaticTemplateTagsError("To use the \'{% static_content %}\' tag you must define the BULB_SFTP_PULL_URL variable in your \'settings.py\' file.")')
            raise BULBStaticTemplateTagsError(
                "To use the '{% static_content %}' tag you must define the BULB_SFTP_PULL_URL variable in your 'settings.py' file.")
