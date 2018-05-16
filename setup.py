from setuptools import setup

setup(
    name='v3oidcmokeyapikey',
    version='0.9.0',
    description='Mokey API Key authentication for OpenStack Identity',
    url='https://github.com/ubccr/v3oidcmokeyapikey',
    author='Martins Innus, Andrew Bruno',
    license='Apache-2.0',
    packages=[
        'v3oidcmokeyapikey',
        'v3oidcmokeyapikey.v3',
    ],
    install_requires=[
        'keystoneauth1',
        'python-keystoneclient',
    ],
    zip_safe=False,
    entry_points={
        "keystoneauth1.plugin": [
            "v3oidcmokeyapikey = v3oidcmokeyapikey._loading:OpenIDConnectMokeyAPIKey",
        ]
    }
)
