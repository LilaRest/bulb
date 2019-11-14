from bulb.contrib.handling.node_models import WebsiteSettings


def website_settings(request):
    return {'WS': WebsiteSettings.get()}
