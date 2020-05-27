from django.conf import settings

def bulb_variables(request):
    return {"DEBUG": settings.DEBUG,
            "BULB_REQUIRES_INITIAL_PATHS": settings.BULB_REQUIRES_INITIAL_PATHS,
            "BULB_BUNDLED_FILES_VERSION": settings.BULB_BUNDLED_FILES_VERSION}
