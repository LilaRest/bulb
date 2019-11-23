from bulb.contrib.auth.decorators import login_required, staff_only
from django.shortcuts import render
from django.conf import settings
import datetime
import os

login_page_url = "/" + settings.BULB_ADMIN_BASEPATH_NAME + "/login"

@staff_only()
@login_required(login_page_url=login_page_url)
def activity_view(request):
    activities = []

    with open(os.path.join(settings.BASE_DIR, "bulb.activity.log")) as log:
        raw_activity_log = log.read()
        split_log = raw_activity_log.split("[BULB ACTIVITY] ")
        del split_log[0]

        for activity in split_log:
            split_activity = activity.split(" : ")
            activity_datetime = datetime.datetime.fromisoformat(split_activity[0].strip("[]")[0:-4])
            split_activity_content = split_activity[1].replace('"', '').replace(u'\n', '').replace(u'\xa0', u' ').split(" | ")
            print(split_activity)
            print(split_activity_content)
            activity_user = split_activity_content[0]
            activity_action = split_activity_content[1]
            activity_node_model = split_activity_content[2]
            activity_instance_uuid = split_activity_content[3]

            activities.append({"datetime": activity_datetime,
                               "user": activity_user,
                               "action": activity_action,
                               "node_model": activity_node_model,
                               "instance_uuid": activity_instance_uuid})

        activities.reverse()

    return render(request, "activity/pages/activity_page.html", {"activities": activities})
