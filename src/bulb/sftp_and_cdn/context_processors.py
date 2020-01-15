from django.conf import settings


def bundled_files_version(request):
    return {'BULB_BUNDLED_FILES_VERSION': settings.BULB_BUNDLED_FILES_VERSION}
