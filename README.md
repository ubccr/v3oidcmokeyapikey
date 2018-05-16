# v3oidcmokeyapikey

OpenStack Keystone plugin for Mokey API key authentication.
[Mokey](https://github.com/ubccr/mokey) is a self-service identity management
portal that sits in front of FreeIPA. Mokey implements a consent endpoint for
[Hydra](https://github.com/ory/hydra) enabling OpenID authentication. When
using Mokey together with Hydra, OpenStack can be configured to use OpenID
authentication for the dashboard. To enable authentication via the OpenStack
CLI users can create an API Key in Mokey. This plugin uses the Mokey API key to
obtain an OIDC authorization code.

## Install

To install run the following commands:

```
$ pip install python-openstackclient
$ pip install git+https://github.com/ubccr/v3oidcmokeyapikey.git
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
