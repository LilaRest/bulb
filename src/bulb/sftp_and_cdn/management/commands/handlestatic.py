from bulb.sftp_and_cdn.exceptions import BULBStaticfilesError
from bulb.utils.log import bulb_logger
from django.core.management.base import BaseCommand
from django.conf import settings
import subprocess


BASE_DIR = settings.BASE_DIR


class Command(BaseCommand):
    args = ''
    help = """
            Collect, clear, bundle and push the staticfiles folder to the SFTP server and purge the CDN if there is one.
            """

    def handle(self, *args, **options):

        if not settings.DEBUG:
            """
            If the command is executed when DEBUG = False, errors can occur from the bulb templatetags.
            Indeed, if DEBUG = False, if {% static_raw_src %}, {% static_bundled_src %} are used, staticfiles will be
            recovered from the SFTP : this will cause that the 'collectstatic command will collect staticfiles from the
            old files on the SFTP, and not from the local new files.
            But also in certain cases, bundled staticfiles will be used : this will cause that the new bundle files will
            be build from the old bundle files.

            See : TODO : add the related documentation page url.
            """
            bulb_logger.error('BULBStaticfilesError("The DEBUG variable must be set on \'True\' to handle new staticfiles.")')
            raise BULBStaticfilesError("The DEBUG variable must be set on 'True' to handle new staticfiles.")

        else:
            # Collect staticfiles.
            print("\n--------------------------")
            print("-- COLLECT STATIC FILES --")
            print("--------------------------\n")

            subprocess.call("python manage.py collectstatic --clear", shell=True)

            # Clear old source staticfiles and purge them on the CDN if there is one.
            subprocess.call("python manage.py clearstatic", shell=True)

            if settings.BULB_SFTP_SRC_STATICFILES_MODE == "raw" or settings.BULB_SFTP_SRC_STATICFILES_MODE == "both":

                # Push new source staticfiles on the SFTP.
                subprocess.call("python manage.py pushstatic --raw", shell=True)

            if settings.BULB_SFTP_SRC_STATICFILES_MODE == "bundled" or settings.BULB_SFTP_SRC_STATICFILES_MODE == "both":

                # Generate the bundled_staticfiles folder which contains all the bundle of the project staticfiles.
                subprocess.call("python manage.py bundlestatic", shell=True)

                # Push new source staticfiles on the SFTP.
                subprocess.call("python manage.py pushstatic --bundled", shell=True)
