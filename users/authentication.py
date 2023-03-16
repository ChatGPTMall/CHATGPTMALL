from rest_framework import authentication
from rest_framework import exceptions
from django.utils.translation import gettext_lazy as _


class BearerAuthentication(authentication.TokenAuthentication):
    """
    Simple token based authentication using username and password

    Clients should authenticate by passing the token key in the 'Authorization'
    HTTP header, prepended with the string 'Bearer '.  For example:

    Authorization: Bearer 956e252a-513c-48c5-92dd-bfddc364e812
    """
    keyword = 'Bearer'

    def authenticate_credentials(self, key):
        model = self.get_model()
        try:
            token = model.objects.select_related('user').get(key=key)
        except model.DoesNotExist:
            raise exceptions.AuthenticationFailed(_('Invalid token.'))

        return token.user, token
