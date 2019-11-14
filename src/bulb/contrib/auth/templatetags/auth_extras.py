from bulb.contrib.auth.node_models import get_user_node_model
from django import template

User = get_user_node_model()

register = template.Library()


@register.filter
def has_perm(user, permission_codename):
    if isinstance(user, User):
        return user.has_perm(permission_codename)
    return False