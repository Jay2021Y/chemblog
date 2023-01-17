from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist


def social_user_signup(username, email):
    try:
        user = User.objects.get(username=username)
    except ObjectDoesNotExist:
        user = User.objects.create_user(username, email)
        user.set_unusable_password()
        user.save()
    return user
