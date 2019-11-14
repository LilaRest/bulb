from django.contrib.auth.hashers import make_password, check_password
from django.conf import settings
import math


def _pepper(password):
    pepper1 = settings.BULB_PEPPER_1
    pepper2 = settings.BULB_PEPPER_2
    password_length = len(password)
    splitted_password = list(password)
    splitted_password.insert(math.floor(password_length / 2), pepper1)
    splitted_password.append(pepper2)
    pepper_password = ''.join(splitted_password)
    return pepper_password


def _hash_password(raw_password):
    hashed_password = make_password(_pepper(raw_password), hasher="bcrypt_sha256")
    return hashed_password


def _check_password(raw_password, encoded_password):
    if check_password(_pepper(raw_password), encoded_password):
        return True
    else:
        return False
