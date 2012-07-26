[identity]
# This section contains configuration options that a variety of Tempest
# test clients use when authenticating with different user/tenant
# combinations

# Set to True if your test environment's Keystone authentication service should
# be accessed over HTTPS
use_ssl = %IDENTITY_USE_SSL%
# This is the main host address of the authentication service API
host = %IDENTITY_HOST%
# Port that the authentication service API is running on
port = %IDENTITY_PORT%
# Version of the authentication service API (a string)
api_version = %IDENTITY_API_VERSION%
# Path to the authentication service tokens resource (do not modify unless you
# have a custom authentication API and are not using Keystone)
path = %IDENTITY_PATH%
# Should typically be left as keystone unless you have a non-Keystone
# authentication API service
strategy = %IDENTITY_STRATEGY%

[compute]
# This section contains configuration options used when executing tests
# against the OpenStack Compute API.

# Allows test cases to create/destroy tenants and users. This option
# enables isolated test cases and better parallel execution,
# but also requires that OpenStack Identity API admin credentials
# are known.
allow_tenant_isolation = %COMPUTE_ALLOW_TENANT_ISOLATION%

# This should be the username of a user WITHOUT administrative privileges
username = %USERNAME%
# The above non-administrative user's password
password = %PASSWORD%
# The above non-administrative user's tenant name
tenant_name = %TENANT_NAME%

# This should be the username of an alternate user WITHOUT
# administrative privileges
alt_username = %ALT_USERNAME%
# The above non-administrative user's password
alt_password = %ALT_PASSWORD%
# The above non-administrative user's tenant name
alt_tenant_name = %ALT_TENANT_NAME%

# Reference data for tests. The ref and ref_alt should be
# distinct images/flavors.
image_ref = %IMAGE_ID%
image_ref_alt = %IMAGE_ID_ALT%
flavor_ref = %FLAVOR_REF%
flavor_ref_alt = %FLAVOR_REF_ALT%

# Number of seconds to wait while looping to check the status of an
# instance or volume that is building.
build_interval = %BUILD_INTERVAL%

# Number of seconds to time out on waiting for an instance or volume
# to build or reach an expected status
build_timeout = %BUILD_TIMEOUT%

# The type of endpoint for a Compute API service. Unless you have a
# custom Keystone service catalog implementation, you probably want to leave
# this value as "compute"
catalog_type = %COMPUTE_CATALOG_TYPE%

# Does the Compute API support creation of images?
create_image_enabled = %COMPUTE_CREATE_IMAGE_ENABLED%

# For resize to work with libvirt/kvm, one of the following must be true:
# Single node: allow_resize_to_same_host=True must be set in nova.conf
# Cluster: the 'nova' user must have scp access between cluster nodes
resize_available = %COMPUTE_RESIZE_AVAILABLE%

# Level to log Compute API request/response details.
log_level = %COMPUTE_LOG_LEVEL%

[image]
# This section contains configuration options used when executing tests
# against the OpenStack Images API

# The type of endpoint for an Image API service. Unless you have a
# custom Keystone service catalog implementation, you probably want to leave
# this value as "image"
catalog_type = %IMAGE_CATALOG_TYPE%

# The version of the OpenStack Images API to use
api_version = %IMAGE_API_VERSION%

# This is the main host address of the Image API
host = %IMAGE_HOST%

# Port that the Image API is running on
port = %IMAGE_PORT%

# This should be the username of a user WITHOUT administrative privileges
username = %USERNAME%
# The above non-administrative user's password
password = %PASSWORD%
# The above non-administrative user's tenant name
tenant_name = %TENANT_NAME%

[compute-admin]
# This section contains configuration options for an administrative
# user of the Compute API. These options are used in tests that stress
# the admin-only parts of the Compute API

# This should be the username of a user WITH administrative privileges
username = %COMPUTE_ADMIN_USERNAME%
# The above administrative user's password
password = %COMPUTE_ADMIN_PASSWORD%
# The above administrative user's tenant name
tenant_name = %COMPUTE_ADMIN_TENANT_NAME%

[identity-admin]
# This section contains configuration options for an administrative
# user of the Compute API. These options are used in tests that stress
# the admin-only parts of the Compute API

# This should be the username of a user WITH administrative privileges
username = %IDENTITY_ADMIN_USERNAME%
# The above administrative user's password
password = %IDENTITY_ADMIN_PASSWORD%
# The above administrative user's tenant name
tenant_name = %IDENTITY_ADMIN_TENANT_NAME%

[whitebox]
# This section contains configuration options for tests to get access to
# internals and deployment of OpenStack infrastructure.
#
# This is the type of Openstack deployment, which could be either:
# 'devstack-local' (default): Devstack running on same host as Tempest
# 'devstack-remote': Devstack installation on hosts other than Tempest host
# 'pkg-multi': Multi node package deployment
openstack_deploy_mode = %WHITEBOX_OPENSTACK_DEPLOY_MODE%
# Connection string to the database of Compute service
compute_db_uri = %WHITEBOX_COMPUTE_DB_URI%
# Connection string to the database of Image Service
glance_db_uri = %WHITEBOX_GLANCE_DB_URI%
# Connection string to the database of Identity Service
keystone_db_uri = %WHITEBOX_KEYSTONE_DB_URI%
# Connection string to the database of Network Service
quantum_db_uri = %WHITEBOX_QUANTUM_DB_URI%
# Path of nova source directory
compute_source_dir = %WHITEBOX_COMPUTE_SOURCE_DIR%
# Path of nova configuration file
compute_config_path = %WHITEBOX_COMPUTE_CONFIG_PATH%
# Directory containing nova binaries such as nova-manage
compute_bin_dir = %WHITEBOX_COMPUTE_BIN_DIR%
# Path to a private key file for SSH access to remote hosts
path_to_private_key = %WHITEBOX_PATH_TO_PRIVATE_KEY%
