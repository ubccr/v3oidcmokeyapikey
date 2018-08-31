from keystoneauth1.identity.v3 import oidc
from keystoneauth1 import exceptions
from random import random
from hashlib import sha256

try:
    from urllib.parse import urlparse, parse_qs
except ImportError:
    from urlparse import urlparse, parse_qs

class OidcMokeyAPIKeyException(exceptions.auth_plugins.AuthPluginException):
    def __init__(self, errmsg):
        self.msg = errmsg
        super(OidcMokeyAPIKeyException, self).__init__(errmsg)

class OidcMokeyAPIKey(oidc.OidcAuthorizationCode):
    """Implementation for OpenID Connect Authorization Code using Mokey API Key."""

    def __init__(self, auth_url, identity_provider, protocol,
                 client_id, api_key, discovery_endpoint,
                 redirect_uri,  **kwargs):
        """The Mokey API Key plugin expects the following.

        :param api_key: Mokey API Key
        :type api_key: string

        :param redirect_uri: OpenID Connect Client Redirect URL
        :type redirect_uri: string

        :param discovery_endpoint: OpenID Connect Discovery Document URL
        :type discovery_endpoint: string

        :param auth_url: URL of the Identity Service
        :type auth_url: string

        :param identity_provider: Name of the Identity Provider the client
                                  will authenticate against
        :type identity_provider: string

        :param client_id: OAuth 2.0 Client ID
        :type client_id: string

        :param protocol: Protocol name as configured in keystone
        :type protocol: string

        """

        super(OidcMokeyAPIKey, self).__init__(
            auth_url, identity_provider, protocol, client_id,
            client_secret=None,
            access_token_endpoint=None,
            discovery_endpoint=discovery_endpoint,
            access_token_type='id_token',
            redirect_uri=redirect_uri,
            code=None,
            **kwargs)
        self.api_key = api_key

    def get_payload(self, session):
        """Get an authorization grant for the "authorization_code" grant type using Mokey API Key.

        :param session: a session object to send out HTTP requests.
        :type session: keystoneauth1.session.Session
        :returns: a python dictionary containing the payload to be exchanged
        :rtype: dict
        """

        code = self._get_auth_code(session)
        payload = {'redirect_uri': self.redirect_uri, 'code': code}

        return payload

    def _get_auth_code(self, session):
        """Exchange a Mokey API key for an Authorization Code"""

        discovery = self._get_discovery_document(session)
        auth_endpoint = discovery.get("authorization_endpoint")
        if auth_endpoint is None:
            raise OidcMokeyAPIKeyException("Failed to find auth endpoint from discovery document")

        state = sha256(str(random()).encode('utf-8')).hexdigest()

        params = {
            'client_id': self.client_id,
            'response_type': 'code',
            'scope': 'openid',
            'state': state,
            'redirect_uri': self.redirect_uri,
        }

        resp = session.get(auth_endpoint,
            params=params, authenticated=False, redirect=False)

        if resp.status_code != 302 or len(resp.headers['Location']) <= 0:
            raise OidcMokeyAPIKeyException("Failed to find redirect url for consent")

        login_url = resp.headers['Location']

        if login_url.startswith(self.redirect_uri):
            qp = parse_qs(urlparse(login_url).query, keep_blank_values=True)
            if 'error_description' in qp:
                raise OidcMokeyAPIKeyException(qp['error_description'][0])

            raise OidcMokeyAPIKeyException('Unknown error')

        headers = {'Authorization': 'Bearer ' + self.api_key, 'Accept': 'application/json'}

        resp = session.get(login_url, headers=headers,
           authenticated=False, redirect=False)

        if resp.status_code != 200:
            raise OidcMokeyAPIKeyException('Failed to GET login url. Status code %s' % resp.status_code)

        login_params = resp.json()

        if 'challenge' not in login_params:
            raise OidcMokeyAPIKeyException('Missing challenge')
        if 'scopes' not in login_params:
            raise OidcMokeyAPIKeyException('Missing scopes')
        if 'csrf' not in login_params:
            raise OidcMokeyAPIKeyException('Missing csrf token')

        payload = {
            'challenge': login_params['challenge'],
            'scope': login_params['scopes'],
            'csrf': login_params['csrf'],
        }

        resp = session.post(login_url, data=payload,
            headers=headers, authenticated=False, redirect=1)

        if resp.status_code != 302 or len(resp.headers['Location']) <= 0:
            raise OidcMokeyAPIKeyException("Failed to find consent url")


        consent_url = resp.headers['Location']

        resp = session.get(consent_url, headers=headers,
           authenticated=False, redirect=1)

        if resp.status_code != 200 and resp.status_code != 302:
            raise OidcMokeyAPIKeyException('Failed to GET consent url. Status code %s' % resp.status_code)

        if resp.status_code == 302:
            consent_url = resp.headers['Location']
        elif resp.status_code == 200:
            consent_params = resp.json()

            if 'challenge' not in consent_params:
                raise OidcMokeyAPIKeyException('Missing challenge')
            if 'scopes' not in consent_params:
                raise OidcMokeyAPIKeyException('Missing scopes')
            if 'csrf' not in consent_params:
                raise OidcMokeyAPIKeyException('Missing csrf token')

            payload = {
                'challenge': consent_params['challenge'],
                'scope': consent_params['scopes'],
                'csrf': consent_params['csrf'],
            }

            resp = session.post(consent_url, data=payload,
                headers=headers, authenticated=False, redirect=1)

            if resp.status_code != 302 or len(resp.headers['Location']) <= 0:
                raise OidcMokeyAPIKeyException("Failed complete oauth2 consent flow")

            consent_url = resp.headers['Location']

        if not consent_url.startswith(self.redirect_uri):
            raise OidcMokeyAPIKeyException("Invalid redirect uri: %s" % consent_url)

        qp = parse_qs(urlparse(consent_url).query, keep_blank_values=True)
        if 'error_description' in qp:
            raise OidcMokeyAPIKeyException(qp['error_description'][0])

        if 'state' not in qp:
            raise OidcMokeyAPIKeyException('State not found %s' % consent_url)

        if qp['state'][0] != state:
            raise OidcMokeyAPIKeyException('Invalid state')

        if 'code' not in qp:
            raise OidcMokeyAPIKeyException('Missing auth code')

        code = qp['code'][0]
        return code
