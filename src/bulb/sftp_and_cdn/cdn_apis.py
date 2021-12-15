from django.conf import settings
import requests
import json


#############
#   CDN77   #
#############

class CDN77:

    @staticmethod
    def purge(paths_list, request_number=None):
        """
        This method send a purge request to the CDN77 API.

        :param paths_list: A list that contains up to 2000 paths to purge.
        :param request_number: The current request number (user for console printing).
        :return: It returns the response of the CDN77 API.
        """
        url = "https://api.cdn77.com/v3/cdn/%s/job/purge" % str(settings.BULB_CDN77_RESOURCE_ID)

        headers = {
            "Authorization": "Bearer %s" % str(settings.BULB_CDN77_API_KEY),
            "Content-Type": "application/json",
        }

        data = json.dumps({
            "paths": paths_list
        })

        print(f"\nAPI PURGE RESPONSE {'n° ' + str(request_number) if request_number is not None else ''}:\n")

        purge_response = requests.post(url=url,
                                       headers=headers,
                                       data=data)

        for key, value in json.loads(purge_response.content).items():
            if key == "url":
                print("     - ", key + " : ")

                for path in value:
                    print("         * ", path)

            else:
                print("     - ", key + " : ", value)

        return purge_response
