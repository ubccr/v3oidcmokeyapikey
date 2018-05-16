import base64
import re
from urlparse import urlparse, parse_qs
from keystoneauth1.identity.v3 import oidc
from keystoneauth1 import exceptions
from random import random
from hashlib import sha256

class OidcMokeyAPIKeyException(exceptions.auth_plugins.AuthPluginException):
    def __init__(self, errmsg):
        self.msg = errmsg
        super(OidcMokeyAPIKeyException, self).__init__(errmsg)

class OidcMokeyAPIKey(oidc.OidcAuthorizationCode):
    """Implementation for OpenID Connect Authorization Code using Mokey API Key."""

    def __init__(self, auth_url, identity_provider, protocol, client_id, api_key, discovery_endpoint, redirect_uri,  **kwargs):
        """Class constructor"""

	super(OidcMokeyAPIKey, self).__init__(auth_url, identity_provider, protocol, client_id, client_secret=None, access_token_endpoint=None, discovery_endpoint=discovery_endpoint, access_token_type='id_token', redirect_uri=redirect_uri, code=None, **kwargs)

        self.api_key = api_key

    def get_payload(self, session):
        """Get an authorization grant for the "authorization_code" grant type using Mokey APIKey.

        :param session: a session object to send out HTTP requests.
        :type session: keystoneauth1.session.Session

        :returns: a python dictionary containing the payload to be exchanged
        :rtype: dict
        """

        discovery = self._get_discovery_document(session)
        auth_endpoint = discovery.get("authorization_endpoint")
        if auth_endpoint is None:
            raise OidcMokeyAPIKeyException("Failed to find auth endpoint from discovery document")

        code = self._get_auth_code(session, auth_endpoint)

        payload = {'redirect_uri': self.redirect_uri, 'code': code}

        return payload


    def _get_auth_code(self, session, auth_endpoint, verify=True):
        """Exchange a Mokey API key for an Authorization Code"""

        state = sha256(str(random())).hexdigest()

        params = {
            'client_id': self.client_id,
            'response_type': 'code',
            'scope': 'openid',
            'state': state,
            'redirect_uri': self.redirect_uri,
        }

        resp = session.get(auth_endpoint,
            params=params, authenticated=False, verify=verify, redirect=False)

        if resp.status_code != 302 or len(resp.headers['Location']) <= 0:
            raise OidcMokeyAPIKeyException("Failed to find redirect url for consent")

        consent_url = resp.headers['Location']

        if consent_url.startswith(self.redirect_uri):
            qp = parse_qs(urlparse(consent_url).query, keep_blank_values=True)
            if 'error_description' in qp:
                raise OidcMokeyAPIKeyException(qp['error_description'][0])

            raise OidcMokeyAPIKeyException('Unknown error')

        headers = {'Authorization': 'Bearer ' + self.api_key, 'Accept': 'application/json'}

        resp = session.get(consent_url, headers=headers,
           authenticated=False, verify=verify, redirect=False)

        if resp.status_code != 200:
            raise OidcMokeyAPIKeyException('Failed to GET consent url. Status code %s' % resp.status_code)

        consent_params = resp.json()

        if 'challenge' not in consent_params:
            raise OidcMokeyAPIKeyException('Missing challenge')
        if 'scopes' not in consent_params:
            raise OidcMokeyAPIKeyException('Missing scopes')
        if 'auth_tok' not in consent_params:
            raise OidcMokeyAPIKeyException('Missing csrf token')

        payload = {
            'challenge': consent_params['challenge'],
            'scope': consent_params['scopes'],
            'auth_tok': consent_params['auth_tok'],
        }

        resp = session.post(consent_url, data=payload,
            headers=headers, authenticated=False, verify=verify, redirect=1)

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
