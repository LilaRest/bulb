from django.template.defaultfilters import register


@register.filter()
def get(instance, parameter):
    value = None
    try:
        if isinstance(instance, dict):
            value = instance[parameter]

        else:
            value = eval(f"{instance}.{parameter}")

    except:
        value = instance.__dict__[parameter]

    finally:
        return value
