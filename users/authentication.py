from rest_framework.authentication import BaseAuthentication, get_authorization_header
from rest_framework import exceptions
from django.utils import timezone
from .models import UserToken


class MultiTokenAuthentication(BaseAuthentication):
    keyword = b'Token'

    def authenticate(self, request):
        auth = get_authorization_header(request).split()
        if not auth or auth[0].lower() != self.keyword.lower():
            return None
        if len(auth) == 1:
            raise exceptions.AuthenticationFailed('Invalid token header. No credentials provided.')
        if len(auth) > 2:
            raise exceptions.AuthenticationFailed('Invalid token header.')

        try:
            key = auth[1].decode()
        except UnicodeError:
            raise exceptions.AuthenticationFailed('Invalid token header.')

        try:
            token = UserToken.objects.select_related('user').get(key=key)
        except UserToken.DoesNotExist:
            raise exceptions.AuthenticationFailed('Invalid token.')

        if not token.user.is_active:
            raise exceptions.AuthenticationFailed('User inactive or deleted.')

        token.last_used = timezone.now()
        token.save(update_fields=['last_used'])
        return (token.user, token)
