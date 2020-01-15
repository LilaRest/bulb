from bulb.contrib.auth.decorators import login_required, staff_only
from django.contrib.staticfiles.finders import find
from django.shortcuts import render
from django.conf import settings
import os

login_page_url = "/" + settings.BULB_ADMIN_BASEPATH_NAME + "/login"


@staff_only()
@login_required(login_page_url=login_page_url)
def releases_view(request):

    releases = ""
    with open(find("releases/releases.txt"), "r") as r:
        for line in r:
            if line != "" and "|" in line:
                split_line = line.split("|")

                # Build version render
                version = f"<p class='version'>{split_line[0]}</p>"

                # Build description render
                description = "<div class='description'>"

                raw_description = split_line[1]

                descriptions_parts = raw_description.split(";")

                for part in descriptions_parts:
                    split_part = part.split(":")

                    # Build part title render
                    part_title = f"<p class='part-title'>{split_part[0]}</p>"
                    description = description + part_title

                    # Build part content render
                    part_content = "<ul class='part-content'>"
                    split_part_content = split_part[1][3:-3].split('", "')

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
