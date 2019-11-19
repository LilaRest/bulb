from bulb.contrib.auth.decorators import login_required, staff_only
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.contrib.staticfiles.finders import find
from django.shortcuts import render
from django.conf import settings
import os

login_page_url = "/" + settings.BULB_ADMIN_BASEPATH_NAME + "/login"

@staff_only()
@login_required(login_page_url=login_page_url)
def releases_view(request):

    releases = ""
    print(find("releases/releases.txt"))

    with open(find("releases/releases.txt"), "r") as r:
        for line in r:
            if line != "" and "|" in line:
                split_line = line.split("|")

                # Build version render
                version = f"<p class='version'>{split_line[0]}</p>"

                # Build description render
                description = "<div class='description'>"

                raw_description = split_line[1]
                print("RAW DESCRIPTION")
                print(raw_description)

                descriptions_parts = raw_description.split(";")
                print("DESCRIPTION PARTS")
                print(descriptions_parts)

                for part in descriptions_parts:
                    print("PART")
                    print(part)
                    split_part = part.split(":")

                    print("split_part")
                    print(split_part)

                    # Build part title render
                    part_title = f"<p class='part-title'>{split_part[0]}</p>"
                    description = description + part_title

                    # Build part content render
                    part_content = "<ul class='part-content'>"
                    split_part_content = split_part[1][3:-3].split('", "')
                    print("split_part_content")
                    print(split_part_content)

                    for element in split_part_content:
                        part_content = part_content + f"<li>{element}</li>"

                    part_content = part_content + "</ul>"
                    description = description + part_content

                description = description + "</div>"

                release = "<div class='release'>" + version + description + "</div>"

                releases = releases + release

            else:
                releases = releases + "<br/>"


    return render(request, "releases/pages/releases_page.html", {"releases": releases})
