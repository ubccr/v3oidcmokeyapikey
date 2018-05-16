# v3oidcmokeyapikey

OpenStack Keystone plugin for Mokey API key authentication.
[Mokey](https://github.com/ubccr/mokey) is a self-service identity management
portal that sits in front of [FreeIPA](https://www.freeipa.org). Mokey
implements a consent endpoint for [Hydra](https://github.com/ory/hydra)
enabling OpenID authentication. When using Mokey together with Hydra, OpenStack
can be configured to use OpenID authentication for the dashboard. To enable
authentication via the OpenStack CLI users can create an API Key in Mokey. This
plugin uses the Mokey API key to obtain an OIDC authorization code.

## Install

To install run the following commands:

```
$ pip install python-openstackclient
$ pip install git+https://github.com/ubccr/v3oidcmokeyapikey.git
```

## Usage

Setup your openrc file to use the v3oidcmokeyapikey plugin. This will use your
Mokey API key to obtain a keystone token and cache for future:

```bash
#!/usr/bin/env bash

unset OS_TOKEN
unset OS_AUTH_TYPE

export OS_API_KEY="my_very_long_mokey_api_key"
export OS_AUTH_URL=https://openstack.example.com:5000/v3
export OS_IDENTITY_API_VERSION=3
export OS_PROJECT_NAME="myproject"
export OS_USERNAME="myuser"
export OS_PROJECT_DOMAIN_NAME="mydomain"
export OS_INTERFACE=public
export OS_REGION_NAME="myregion"

export OS_TOKEN=`openstack --os-auth-type v3oidcmokeyapikey \
                           --os-identity-provider myprovider \
                           --os-protocol openid \
                           --os-discovery-endpoint https://sso.example.com/.well-known/openid-configuration \
                           --os-client-id my_client_id \
                           --os-redirect-uri https://localhost/somestring \
                                token issue -f value -c id`

export OS_AUTH_TYPE=v3token
```

## Developing and Testing

To develop and run the unit tests:

```
$ virtualenv venv
$ source venv/bin/activate

$ git clone git@github.com:ubccr/v3oidcmokeyapikey.git
$ cd v3oidcmokeyapikey
$ python setup.py develop

$ export OS_REDIRECT_URI=https://localhost/test
$ export OS_CLIENT_ID=test-client
$ export OS_API_KEY=xxxx
$ export OS_DISCOVERY_ENDPOINT=https://hydra.localhost/.well-known/openid-configuration
$ export REQUESTS_CA_BUNDLE=ca.crt

$ python -m testtools.run tests.test_v3oidcmokeyapikey
```
