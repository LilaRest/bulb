from bulb.sftp_and_cdn.exceptions import BULBStaticfilesError
from bulb.utils import get_folders_paths_list
from bulb.sftp_and_cdn.sftp import SFTP
from bulb.utils.log import bulb_logger
from django.core.management.base import BaseCommand
from django.template import Template, Context
from django.conf import settings
import subprocess
import lxml.html
import json
import uuid
import os

BASE_DIR = settings.BASE_DIR


class Command(BaseCommand):
    args = ''
    help = """
            Collect, clear, bundle and push the staticfiles folder to the SFTP server and purge the CDN if there is one.
            """
    def add_arguments(self, parser):
        parser.add_argument("-a", "--added", type=str)
        parser.add_argument("-m", "--modified", type=str)
        parser.add_argument("-r", "--removed", type=str)

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
            added_files_paths = None
            modified_files_paths = None
            removed_files_paths = None

            # Prevent errors if datas are corrupted.
            try:
                added_files_paths = json.loads(options["added"])

            except:
                pass

            try:
                modified_files_paths = json.loads(options["modified"])

            except:
                pass

            try:
                removed_files_paths = json.loads(options["removed"])

            except:
                pass

            print("added_files_paths")
            print(added_files_paths)
            print("modified_files_paths")
            print(modified_files_paths)
            print("removed_files_paths")
            print(removed_files_paths)

            # Collect staticfiles.
            print("\n--------------------------")
            print("-- COLLECT STATIC FILES --")
            print("--------------------------\n")

            subprocess.call("python manage.py collectstatic --clear --noinput", shell=True)

            if not added_files_paths and not modified_files_paths and not removed_files_paths:

                # Remove old source staticfiles and collect them in a list to purge them on the CDN at the end.
                raw_files_to_purge_list = SFTP.clear_src_staticfiles(src_type="raw", no_purge=True)
                bundled_files_to_purge_list = SFTP.clear_src_staticfiles(src_type="bundled", no_purge=True)
                files_to_purge_list = raw_files_to_purge_list + bundled_files_to_purge_list

                if settings.BULB_SFTP_SRC_STATICFILES_MODE == "raw" or settings.BULB_SFTP_SRC_STATICFILES_MODE == "both":

                    # Push new source staticfiles on the SFTP.
                    subprocess.call("python manage.py pushstatic --raw", shell=True)

                if settings.BULB_SFTP_SRC_STATICFILES_MODE == "bundled" or settings.BULB_SFTP_SRC_STATICFILES_MODE == "both":

                    # Generate the bundled_staticfiles folder which contains all the bundle of the project staticfiles.
                    subprocess.call("python manage.py bundlestatic", shell=True)

                    # Push new source staticfiles on the SFTP.
                    subprocess.call("python manage.py pushstatic --bundled", shell=True)

                # Purge all old staticfiles.
                SFTP.purge_src_staticfiles(files_to_purge_list=files_to_purge_list)

            else:
                # 'amr' = added, modified or removed
                amr_files_paths = []
                amr_files_paths += added_files_paths if added_files_paths is not None else []
                amr_files_paths += modified_files_paths if modified_files_paths is not None else []
                amr_files_paths += removed_files_paths if removed_files_paths is not None else []
                print("amr_files_paths")
                print(amr_files_paths)

                # Remove doublons.
                amr_files_paths = list(set(amr_files_paths))
                print("amr_files_paths 2")
                print(amr_files_paths)

                # Collect all elements(pages, module, etc.) with their associated staticifiles.
                pages = {}

                # Get paths of all "pages" folders of the project.
                pages_folders_paths = get_folders_paths_list("pages")

                # Loop on each "pages" folders of the project.
                for pages_folder_path in pages_folders_paths:

                    splitted_pages_folder_path = pages_folder_path.split("/")

                    # Get the parent folder name and build its future path in the bundled_staticfiles folder.
                    application_name = splitted_pages_folder_path[-2] if splitted_pages_folder_path[-2] != "templates" else splitted_pages_folder_path[-3]

                    if not application_name in pages.keys():
                        pages[application_name] = {}

                    # Retrieve all pages with their associated staticfiles' paths.
                    for root, dirs, files in os.walk(pages_folder_path):

                        for file in files:

                            if not file in pages[application_name].keys():
                                pages[application_name][file] = []

                            file_path = pages_folder_path + "/" + file

                            template_content = None
                            with open(file_path, "r") as template_file:
                                template_content = template_file.read()
                                template_content = template_content.replace('{% url', 'xxx')

                            template_object = Template(template_content)
                            context = Context({"DEBUG": True, "BULB_REQUIRES_INITIAL_PATHS": True})
                            template = template_object.render(context)
                            doc = lxml.html.document_fromstring(template)

                            links = doc.xpath("//link[@rel='stylesheet']")

                            # Add CSS dependencies to the entry.js file.
                            for link in links:
                                href_value = link.get("href")

                                # Ignore href with external urls.
                                if href_value[:4] == "http":
                                    continue

                                else:
                                    related_staticfile_path = href_value.split("/")[-1]
                                    pages[application_name][file].append(related_staticfile_path)

                            # Add JS dependencies to the entry.js file.
                            scripts = doc.xpath("//script")

                            for script in scripts:
                                src_value = script.get("src")

                                # Ignore href with external urls.
                                if src_value is None:
                                    continue

                                elif src_value[:4] == "http":
                                    continue

                                else:
                                    related_staticfile_path = href_value.split("/")[-1]
                                    pages[application_name][file].append(related_staticfile_path)


                # # Prevent wrong staticfiles' paths format.
                # for path in amr_files_paths:
                #
                #     # Ignore all files that are not staticfiles.
                #     if path[-3:] == ".js" or path[-4:] == ".css" or path[-5:] == ".sass" or path[-5:] == ".scss":
                #
                #         # Uniformize path's format.
                #         if path[0] == "/":
                #             path = path[1:]
                #
                #         splitted_path = path.split("/")
                #
                #         # Find application and element (page, element, module, etc.) names.
                #         application_name = None
                #         element_name = None
                #
                #         if splitted_path[0] != "www" or splitted_path[1] != "staticfiles":
                #             if splitted_path[1] == splitted_path[3]:
                #                 application_name = splitted_path[1]
                #                 element_name = splitted_path[6].split(".")[0]
                #
                #         else:
                #             application_name = splitted_path[4]
                #             element_name = splitted_path[5].split(".")[0]
                #
                #         if application_name is not None and element_name is not None:
                #
                #             if not application_name in pages_to_refresh.keys():
                #                 pages_to_refresh[application_name] = []
                #
                #             if not element_name in pages_to_refresh[application_name]:
                #                 pages_to_refresh[application_name].append(element_name)
                #
                #
                # print("pages_to_refresh (APRÈS FORMATTAGE)")
                # print(pages_to_refresh)

                # Retrieve the list of pages to resfresh in two different formats (for the bundle an clear commands).
                pages_to_refresh_paths = []
                pages_to_refresh_names = {}

                # Prevent wrong staticfiles' paths format.
                for path in amr_files_paths:

                    # Ignore all files that are not staticfiles.
                    if path[-3:] == ".js" or path[-4:] == ".css" or path[-5:] == ".sass" or path[-5:] == ".scss":

                        # Uniformize path's format.
                        if path[0] == "/":
                            path = path[1:]

                        splitted_path = path.split("/")

                        # Find application and element (page, element, module, etc.) names.
                        application_name = None
                        element_name = None

                        if splitted_path[0] != "www" or splitted_path[1] != "staticfiles":
                            if splitted_path[1] == splitted_path[3]:
                                application_name = splitted_path[1]
                                element_name = splitted_path[-1]


                        else:
                            application_name = splitted_path[4]
                            element_name = splitted_path[-1]

                        if application_name is not None and element_name is not None:

                            for page_path, staticfiles_names in pages[application_name].items():
                                for staticfiles_name in staticfiles_names:
                                    if staticfiles_name == element_name:

                                        if not path in pages_to_refresh_path:
                                            pages_to_refresh_paths.append(path)

                                        if not element_name in pages_to_refresh_names:
                                            if not application_name in pages_to_refresh_names.keys():
                                                pages_to_refresh_names[application_name] = []

                                            pages_to_refresh_names[application_name].append(element_name.split(".")[0])


                print("pages")
                print(pages)
                print("pages_to_refresh_names")
                print(pages_to_refresh_names)
                print("pages_to_refresh_paths")
                print(pages_to_refresh_paths)

                # Remove old source staticfiles and collect them in a list to purge them on the CDN at the end.
                files_to_purge_list = SFTP.clear_src_staticfiles(no_purge=True, pages_to_refresh_names=pages_to_refresh_names)

                if settings.BULB_SFTP_SRC_STATICFILES_MODE == "raw" or settings.BULB_SFTP_SRC_STATICFILES_MODE == "both":

                    # Push new source staticfiles on the SFTP.
                    subprocess.call(f"python manage.py pushstatic --raw --pages-to-refresh-names {json.dumps(pages_to_refresh_names)}", shell=True)

                if settings.BULB_SFTP_SRC_STATICFILES_MODE == "bundled" or settings.BULB_SFTP_SRC_STATICFILES_MODE == "both":

                    # Generate the bundled_staticfiles folder which contains all the bundle of the project staticfiles.
                    subprocess.call("python manage.py bundlestatic --pages-to-refresh-paths {json.dumps(pages_to_refresh_paths)}", shell=True)

                    # Push new source staticfiles on the SFTP.
                    subprocess.call("python manage.py pushstatic --bundled --pages-to-refresh-names {json.dumps(pages_to_refresh_names)}", shell=True)

                # Purge all old staticfiles.
                if files_to_purge_list:
                    SFTP.purge_src_staticfiles(files_to_purge_list=files_to_purge_list)
