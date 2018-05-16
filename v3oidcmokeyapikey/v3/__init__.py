from v3oidcmokeyapikey.v3 import apikey

_APIKEY_AVAILABLE = apikey is not None

OidcMokeyAPIKey = apikey.OidcMokeyAPIKey

__all__ = ('OidcMokeyAPIKey',)
