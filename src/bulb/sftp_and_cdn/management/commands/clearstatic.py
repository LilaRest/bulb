from bulb.sftp_and_cdn.sftp import SFTP
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    args = ''
    help = """
            Clear (remove) the raw_src or the bundled_src folder on the SFTP server and purge the CDN if there is one.
           """

    def add_arguments(self, parser):
        parser.add_argument("-r", "--raw", action="store_true")
        parser.add_argument("-b", "--bundled", action="store_true")
        parser.add_argument("-p", "--no-purge", action="store_true")

    def handle(self, *args, **kwargs):
        if kwargs["raw"]:
            SFTP.clear_src_staticfiles(src_type="raw", no_purge=kwargs["purge"])

        if kwargs["bundled"]:
            SFTP.clear_src_staticfiles(src_type="bundled", no_purge=kwargs["purge"])

        if not kwargs["raw"] and not kwargs["bundled"]:
            SFTP.clear_src_staticfiles(src_type="raw", no_purge=kwargs["purge"])
            SFTP.clear_src_staticfiles(src_type="bundled", no_purge=kwargs["purge"])
