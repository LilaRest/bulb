from bulb.contrib.auth.node_models import get_user_node_model, get_anonymoususer_node_model
from django.contrib.messages import add_message, SUCCESS, ERROR
from django.shortcuts import redirect
from django.conf import settings

User = get_user_node_model()
AnonymousUser = get_anonymoususer_node_model()


def email_confirmation_view(request, email_confirmation_key):
    user = User.get(email_confirmation_key=email_confirmation_key)

    if not isinstance(user, AnonymousUser):
        user.update("email_confirmation_key", "validated")
        user.update("email_is_confirmed", True)
        add_message(request, SUCCESS, "Votre adresse email a bien été confirmée. Vous pouvez maintenant vous connecter")

    else:
        add_message(request, ERROR, "Le lien de confirmation est incorrect ou a expiré.")

    return redirect(settings.BULB_LOGIN_URL, permanent=True)
