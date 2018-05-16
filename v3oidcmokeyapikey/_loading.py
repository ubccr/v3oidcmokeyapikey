# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import v3oidcmokeyapikey
from keystoneauth1 import loading
from keystoneauth1.loading._plugins.identity import v3

class OpenIDConnectMokeyAPIKey(v3._OpenIDConnectBase):

    @property
    def plugin_class(self):
        return v3oidcmokeyapikey.OpenIDConnectMokeyAPIKey

    @property
    def available(self):
        return v3oidcmokeyapikey._APIKEY_AVAILABLE

    def get_options(self):
        options = super(OpenIDConnectMokeyAPIKey, self).get_options()

        options.extend([
            loading.Opt('redirect-uri', required=True, help='OpenID Connect Redirect URL'),
            loading.Opt('api-key', required=True, secret=True, help='API Key')
        ])

        return options
