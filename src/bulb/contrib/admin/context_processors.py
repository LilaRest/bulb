from django.conf import settings


def additionnal_admin_modules(request):
    return {"BULB_ADDITIONAL_ADMIN_MODULES": settings.BULB_ADDITIONAL_ADMIN_MODULES}
