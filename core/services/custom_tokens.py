from rest_framework_simplejwt.tokens import AccessToken, BlacklistMixin

class BlacklistableAccessToken(BlacklistMixin, AccessToken):
    pass
