from bulb.sftp_and_cdn.exceptions import BULBStaticfilesError
from bulb.utils import get_folders_paths_list
from bulb.sftp_and_cdn.sftp import SFTP
from bulb.utils.log import bulb_logger
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    args = ''
    help = """
            Push source staticfiles folder to the SFTP server.
            """

    def add_arguments(self, parser):
        parser.add_argument("-r", "--raw", action="store_true")
        parser.add_argument("-b", "--bundled", action="store_true")

    def handle(self, *args, **kwargs):

        # Get the staticfiles folder path
        raw_staticfiles_folder_path = get_folders_paths_list("staticfiles")

        if raw_staticfiles_folder_path is not None:
            bundled_staticfiles_folder_path = get_folders_paths_list("bundled_staticfiles")

            if kwargs["raw"]:
                SFTP.push_src_staticfiles(src_type="raw",
                                          local_staticfiles_folder_path=raw_staticfiles_folder_path)

            if kwargs["bundled"]:
                if bundled_staticfiles_folder_path is not None:
                    SFTP.push_src_staticfiles(src_type="bundled",
                                              local_staticfiles_folder_path=bundled_staticfiles_folder_path)

                else:
                    bulb_logger.error(
                        'BULBStaticfilesError("The bundled_staticfiles folder was not found. Please execute the \'collectstatic\' and \'bundlestatic\' commands before pushing it to your sftp server.")')
                    raise BULBStaticfilesError(
                        "The bundled_staticfiles folder was not found. Please execute the 'collectstatic' and 'bundlestatic' commands before pushing it to your sftp server.")

            if not kwargs["raw"] and not kwargs["bundled"]:
                SFTP.push_src_staticfiles(src_type="raw",
                                          local_staticfiles_folder_path=raw_staticfiles_folder_path)

                if bundled_staticfiles_folder_path is not None:
                    SFTP.push_src_staticfiles(src_type="bundled",
                                              local_staticfiles_folder_path=bundled_staticfiles_folder_path)
                else:
                    bulb_logger.error(
                        'BULBStaticfilesError("The bundled_staticfiles folder was not found. Please execute the \'collectstatic\' and \'bundlestatic\' commands before pushing it to your sftp server.")')
                    raise BULBStaticfilesError(
                        "The bundled_staticfiles folder was not found. Please execute the 'collectstatic' and 'bundlestatic' commands before pushing it to your sftp server.")
        else:
            bulb_logger.error(
                'BULBStaticfilesError("The staticfiles folder was not found. Please execute the \'collectstatic\' command before pushing it to your sftp server.")')
            raise BULBStaticfilesError(
                "The staticfiles folder was not found. Please execute the 'collectstatic' command before pushing it to your sftp server.")
