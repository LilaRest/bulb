from bulb.sftp_and_cdn.exceptions import BULBStaticfilesError
from bulb.utils import get_folders_paths_list
from bulb.utils.log import bulb_logger
import bulb
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
            Generate the bundled_staticfiles folder which contains all the bundle of the project staticfiles.
            """

    def add_arguments(self, parser):
        parser.add_argument("-m", "--pages-to-refresh-names", type=str)

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
            bulb_logger.error(
                'BULBStaticfilesError("The DEBUG variable must be set on \'True\' to handle new staticfiles.")')
            raise BULBStaticfilesError("The DEBUG variable must be set on 'True' to handle new staticfiles.")

        else:
            # Bundling temporary files paths :
            package_file_path = None
            package_lock_file_path = None
            babelrc_file_path = None
            entry_file_path = None
            webpack_config_file_path = None

            # Test if the staticfiles folder exist.
            if not os.path.isdir(os.path.join(BASE_DIR, "staticfiles")):
                bulb_logger.error(
                    'BULBStaticfilesError("The \'staticfiles\' folder was not found. Please run the \'python manage.py collectstatic\' command.")')
                raise BULBStaticfilesError(
                    "The 'staticfiles' folder was not found. Please run the 'python manage.py collectstatic' command.")

            else:
                # Prevent errors if datas are corrupted.
                try:
                    bulb_path = bulb.__path__[0]

                    # Create the package.json file.
                    package_file_path = os.path.join(BASE_DIR, "package.json")
                    package_lock_file_path = os.path.join(BASE_DIR, "package-lock.json")
                    package_file = open(package_file_path, "w")
                    package_file.write(open(bulb_path + "/sftp_and_cdn/webpack_files/package.json", "r").read())
                    package_file.close()

                    # Create the .babelrc file.
                    babelrc_file_path = os.path.join(BASE_DIR, ".babelrc")
                    babelrc_file = open(babelrc_file_path, "w")
                    babelrc_file.write(open(bulb_path + "/sftp_and_cdn/webpack_files/.babelrc", "r").read())
                    babelrc_file.close()

                    # Install npm dependencies
                    subprocess.call(f"npm install", shell=True)

                    # Get paths of all "pages" folders of the project.
                    pages_folders_paths = get_folders_paths_list("pages")
                    print("pages_folders_paths")
                    print(pages_folders_paths)

                    # Get pages to refresh.
                    pages_to_refresh_names = None
                    if "pages-to-refresh-names" in options:
                        try:
                            pages_to_refresh_names = json.loads(options["pages-to-refresh-names"])

                        except:
                            pass

                    print("pages_to_refresh_names")
                    print(pages_to_refresh_names)

                    # Get the bundled_staticfiles folder path.
                    bundled_staticfiles_folder_path = os.path.join(BASE_DIR, "bundled_staticfiles")

                    # Remove the old bundled_staticfiles folder and create a new one.
                    subprocess.call(f"rm -rf {bundled_staticfiles_folder_path}", shell=True)
                    os.mkdir(bundled_staticfiles_folder_path)

                    print("\n--------------")
                    print("-- BUNDLING --")
                    print("--------------\n")

                    # Loop on each "pages" folders of the project.
                    for pages_folder_path in pages_folders_paths:

                        splitted_pages_folder_path = pages_folder_path.split("/")

                        # Get the parent folder name and build its future path in the bundled_staticfiles folder.
                        parent_folder_name = splitted_pages_folder_path[-2] if splitted_pages_folder_path[-2] != "templates" else splitted_pages_folder_path[-3]
                        parent_folder_path = bundled_staticfiles_folder_path + "/" + parent_folder_name

                        print("\n     " + ("-" * (len(parent_folder_name) + 6)))
                        print("     -- " + parent_folder_name.upper() + " --")
                        print("     " + ("-" * (len(parent_folder_name) + 6)) + "\n")

                        # Create the current parent folder in the bundled_staticifiles folder.
                        os.mkdir(parent_folder_path)
                        print("mkdir ok !")

                        # Loop on each page of the current "pages" folder, get their dependencies and bundle them.
                        def bundle_file_staticfiles(file):
                            print("bfs is executed")
                            file_path = pages_folder_path + "/" + file

                            print("\n           -", file)

                            template_content = None
                            with open(file_path, "r") as template_file:
                                template_content = template_file.read()
                                template_content = template_content.replace('{% url', 'xxx')

                            template_object = Template(template_content)
                            context = Context({"DEBUG": True})
                            template = template_object.render(context)
                            doc = lxml.html.document_fromstring(template)

                            # Create the entry.js file.
                            entry_file_path = os.path.join(BASE_DIR, "entry.js")
                            entry_file = open(entry_file_path, "a")

                            # Add polyfill dependencies to the entry.js file.
                            if settings.BULB_SRC_BUNDLES_USE_WEBPACK_POLYFILL:
                                entry_file.write("import 'core-js';import 'regenerator-runtime/runtime';")

                            print("\n               Searching CSS dependencies...")
                            print("               Found :\n")

                            links = doc.xpath("//link[@rel='stylesheet']")

                            # Add CSS dependencies to the entry.js file.
                            for link in links:
                                href_value = link.get("href")
                                print("                 -", href_value)

                                # Ignore href with external urls.
                                if href_value[:4] == "http":
                                    continue

                                else:
                                    related_staticfiles_path = "." + "/staticfiles" + href_value[7:]

                                    entry_file.write(f"import {'a' + uuid.uuid4().hex} from '{related_staticfiles_path}';")

                            # Add JS dependencies to the entry.js file.
                            print("\n               Searching JS dependencies...")
                            print("               Found :\n")

                            scripts = doc.xpath("//script")

                            for script in scripts:
                                src_value = script.get("src")
                                print("                 -", src_value)

                                # Ignore href with external urls.
                                if src_value is None:
                                    continue

                                elif src_value[:4] == "http":
                                    continue

                                else:
                                    related_staticfiles_path = "." + "/staticfiles" + src_value[7:]

                                    entry_file.write(f"import {'a' + uuid.uuid4().hex} from '{related_staticfiles_path}';")

                            entry_file.close()

                            print("\n               ------------------------")
                            print("               -- INITIALIZE WEBPACK --")
                            print("               ------------------------\n")

                            # Create webpack.config.js file.
                            webpack_config_file_path = os.path.join(BASE_DIR, "webpack.config.js")
                            webpack_config_file = open(webpack_config_file_path, "a")
                            bundle_name = file[:-5]

                            # Add file version.
                            bulb_bundled_files_version = settings.BULB_BUNDLED_FILES_VERSION
                            if bulb_bundled_files_version is not None:
                                bundle_name = bundle_name + "&V=" + str(bulb_bundled_files_version)

                            webpack_config_file.write(f"""// Don't modify this file, it is generated by a bulb's script (see sftp_and_cdn.management.commands.handlestatic.py)
    process.env.WEBPACK_ENTRY = ['{entry_file_path}'];
    process.env.WEBPACK_OUTPUT = '{parent_folder_path}';
    process.env.BUNDLE_NAME = '{bundle_name}';

    """)
                            webpack_config_file.write(open(bulb_path + "/sftp_and_cdn/webpack_files/webpack.config.js", "r").read())
                            webpack_config_file.close()

                            print("                     Done ✔ ")

                            print("\n               ---------------------")
                            print("               -- RUN WEBPACK --")
                            print("               ---------------------\n")

                            subprocess.call(f"npm run build", shell=True)

                            # Remove the entry.js file.
                            os.remove(entry_file_path)

                            # # Remove the webpack.config.js file.
                            os.remove(webpack_config_file_path)

                        for root, dirs, files in os.walk(pages_folder_path):

                            for file in files:

                                if not pages_to_refresh_names:
                                    bundle_file_staticfiles(file)

                                else:
                                    for page in pages_to_refresh_names:
                                        if file == page:
                                            bundle_file_staticfiles(file)
                                            break

                    # Remove the .babelrc file
                    os.remove(babelrc_file_path)

                    # # Remove the package.json and package-lock.json files.
                    os.remove(package_file_path)
                    os.remove(package_lock_file_path)

                    return bundled_staticfiles_folder_path

                # If any error occurs during bundling, all the temporary files are removed.
                except:

                    # Remove the entry.js file.
                    try:
                        os.remove(entry_file_path)

                    except (FileNotFoundError, TypeError):
                        pass

                    # # Remove the webpack.config.js file.
                    try:
                        os.remove(webpack_config_file_path)

                    except (FileNotFoundError, TypeError):
                        pass

                    # Remove the .babelrc file.
                    try:
                        os.remove(babelrc_file_path)

                    except (FileNotFoundError, TypeError):
                        pass

                    # # Remove the package.json and package-lock.json files.
                    try:
                        os.remove(package_file_path)

                    except FileNotFoundError:
                        pass

                    try:
                        os.remove(package_lock_file_path)

                    except (FileNotFoundError, TypeError):
                        pass

                    # bulb_logger.error("FileNotFoundError or TypeError")
                    # raise
