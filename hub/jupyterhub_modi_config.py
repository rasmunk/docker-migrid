# Example config
from jhubauthenticators import RegexUsernameParser, JSONParser
from ldap_spawner_hooks import setup_ldap_user
from ldap_spawner_hooks import LDAP, LDAP_SEARCH_ATTRIBUTE, SPAWNER_LDAP_OBJECT_ATTRIBUTE
c = get_config()

c.JupyterHub.ip = '0.0.0.0'
c.JupyterHub.hub_ip = '0.0.0.0'
c.JupyterHub.port = 80
c.JupyterHub.base_url = '/modi'

# Spawner setup
c.JupyterHub.spawner_class = 'dockerspawner.DockerSpawner'
c.DockerSpawner.image = 'nielsbohr/base-notebook:latest'
c.DockerSpawner.remove_containers = True
c.DockerSpawner.network_name = 'docker-migrid_default'
c.DockerSpawner.environment = {'JUPYTER_ENABLE_LAB': '1',
                               'NB_GID': '100',
                               'CHOWN_HOME': 'yes',
                               'CHOWN_HOME_OPTS': '-R'}
c.DockerSpawner.pre_spawn_hook = setup_ldap_user

# Authenticator setup
c.JupyterHub.authenticator_class = 'jhubauthenticators.HeaderAuthenticator'
c.HeaderAuthenticator.enable_auth_state = True
c.HeaderAuthenticator.allowed_headers = {'auth': 'Remote-User',
                                         'userid': 'User'}
c.HeaderAuthenticator.header_parser_classes = {'auth': RegexUsernameParser,
                                               'userid': JSONParser}
# Email regex
RegexUsernameParser.username_extract_regex = '([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)'

# Define LDAP connection options
LDAP.url = "openldap"
LDAP.user = "cn=admin,dc=migrid,dc=org"
LDAP.password = "dummyldap_password"
LDAP.base_dn = "dc=migrid,dc=org"

# LDAP get dn to submit to the DIT
# LDAP.submit_spawner_attribute = 'user.variable'
LDAP.submit_user_auth_state_selector = ('User', 'CERT')

# Prepare LDAP object
LDAP.replace_object_with = {'/': '+'}

# Attribute and where the information is from
LDAP.dynamic_attributes = {
    'emailAddress': SPAWNER_LDAP_OBJECT_ATTRIBUTE,
    'nextUidNumber': LDAP_SEARCH_ATTRIBUTE
}

LDAP.set_spawner_attributes = {
    'environment': {'NB_USER': '{emailAddress}',
                    'NB_UID': '{nextUidNumber}'},
}

# Attributes used to check whether the ldap data of type object_classes already exists
LDAP.unique_object_attributes = ['emailAddress']
LDAP.search_attribute_queries = [{'search_base': LDAP.base_dn,
                                  'search_filter': '(objectclass=X-nextUserIdentifier)',
                                  'attributes': ['uidNumber']}]
# Submit object settings
LDAP.object_classes = ['X-certsDistinguishedName', 'PosixAccount']
LDAP.object_attributes = {'uid': '{emailAddress}',
                          'uidNumber': '{nextUidNumber}',
                          'gidNumber': '100',
                          'homeDirectory': '/home/{emailAddress}'}