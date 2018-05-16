from testtools import TestCase
from v3oidcmokeyapikey.v3 import apikey
from keystoneauth1 import session
import os

class TestV3MokeyAPIKey(TestCase):
    def setUp(self):
        super(TestV3MokeyAPIKey, self).setUp()
        self.session = session.Session()

        for k in ['OS_CLIENT_ID', 'OS_DISCOVERY_ENDPOINT', 'OS_API_KEY', 'OS_REDIRECT_URI']:
            if k not in os.environ:
                self.skipTest('{} not found'.format(k))

        self.client_id = os.environ['OS_CLIENT_ID']
        self.discovery_endpoint = os.environ['OS_DISCOVERY_ENDPOINT']
        self.redirect_uri = os.environ['OS_REDIRECT_URI']
        self.api_key = os.environ['OS_API_KEY']

    def test_auth_code(self):
        a = apikey.OidcMokeyAPIKey("", "", "", self.client_id, self.api_key, self.discovery_endpoint, self.redirect_uri)
        code = a._get_auth_code(self.session)
        #TODO add better check here
        assert len(code) > 1
