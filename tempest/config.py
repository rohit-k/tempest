# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2012 OpenStack, LLC
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import ConfigParser
import logging
import os

from tempest.common.utils import data_utils

LOG = logging.getLogger(__name__)


class BaseConfig(object):

    SECTION_NAME = None

    def __init__(self, conf):
        self.conf = conf

    def get(self, item_name, default_value=None):
        try:
            return self.conf.get(self.SECTION_NAME, item_name, raw=True)
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
            return default_value


class IdentityConfig(BaseConfig):

    """Provides configuration information for authenticating with Keystone."""

    SECTION_NAME = "identity"

    @property
    def catalog_type(self):
        """Catalog type of the Identity service."""
        return self.get("catalog_type", 'identity')

    @property
    def host(self):
        """Host IP for making Identity API requests."""
        return self.get("host", "127.0.0.1")

    @property
    def port(self):
        """Port for the Identity service."""
        return self.get("port", "8773")

    @property
    def api_version(self):
        """Version of the Identity API"""
        return self.get("api_version", "v1.1")

    @property
    def path(self):
        """Path of API request"""
        return self.get("path", "/")

    @property
    def auth_url(self):
        """The Identity URL (derived)"""
        auth_url = data_utils.build_url(self.host,
                                        self.port,
                                        self.api_version,
                                        self.path,
                                        use_ssl=self.use_ssl)
        return auth_url

    @property
    def use_ssl(self):
        """Specifies if we are using https."""
        return self.get("use_ssl", 'false').lower() != 'false'

    @property
    def strategy(self):
        """Which auth method does the environment use? (basic|keystone)"""
        return self.get("strategy", 'keystone')


class IdentityAdminConfig(BaseConfig):

    SECTION_NAME = "identity-admin"

    @property
    def username(self):
        """Username to use for Identity Admin API requests"""
        return self.get("username", "admin")

    @property
    def tenant_name(self):
        """Tenant name to use for Identity Admin API requests"""
        return self.get("tenant_name", "admin")

    @property
    def password(self):
        """API key to use for Identity Admin API requests"""
        return self.get("password", "pass")


class ComputeConfig(BaseConfig):

    SECTION_NAME = "compute"

    @property
    def allow_tenant_isolation(self):
        """
        Allows test cases to create/destroy tenants and users. This option
        enables isolated test cases and better parallel execution,
        but also requires that OpenStack Identity API admin credentials
        are known.
        """
        return self.get("allow_tenant_isolation", 'false').lower() != 'false'

    @property
    def username(self):
        """Username to use for Nova API requests."""
        return self.get("username", "demo")

    @property
    def tenant_name(self):
        """Tenant name to use for Nova API requests."""
        return self.get("tenant_name", "demo")

    @property
    def password(self):
        """API key to use when authenticating."""
        return self.get("password", "pass")

    @property
    def alt_username(self):
        """Username of alternate user to use for Nova API requests."""
        return self.get("alt_username")

    @property
    def alt_tenant_name(self):
        """Alternate user's Tenant name to use for Nova API requests."""
        return self.get("alt_tenant_name")

    @property
    def alt_password(self):
        """API key to use when authenticating as alternate user."""
        return self.get("alt_password")

    @property
    def image_ref(self):
        """Valid primary image to use in tests."""
        return self.get("image_ref", "{$IMAGE_ID}")

    @property
    def image_ref_alt(self):
        """Valid secondary image reference to be used in tests."""
        return self.get("image_ref_alt", "{$IMAGE_ID_ALT}")

    @property
    def flavor_ref(self):
        """Valid primary flavor to use in tests."""
        return self.get("flavor_ref", 1)

    @property
    def flavor_ref_alt(self):
        """Valid secondary flavor to be used in tests."""
        return self.get("flavor_ref_alt", 2)

    @property
    def resize_available(self):
        """Does the test environment support resizing?"""
        return self.get("resize_available", 'false').lower() != 'false'

    @property
    def create_image_enabled(self):
        """Does the test environment support snapshots?"""
        return self.get("create_image_enabled", 'false').lower() != 'false'

    @property
    def build_interval(self):
        """Time in seconds between build status checks."""
        return float(self.get("build_interval", 10))

    @property
    def build_timeout(self):
        """Timeout in seconds to wait for an entity to build."""
        return float(self.get("build_timeout", 300))

    @property
    def run_ssh(self):
        """Does the test environment support snapshots?"""
        return self.get("run_ssh", 'false').lower() != 'false'

    @property
    def ssh_user(self):
        """User name used to authenticate to an instance."""
        return self.get("ssh_user", "root")

    @property
    def ssh_timeout(self):
        """Timeout in seconds to wait for authentcation to succeed."""
        return float(self.get("ssh_timeout", 300))

    @property
    def network_for_ssh(self):
        """Network used for SSH connections."""
        return self.get("network_for_ssh", "public")

    @property
    def ip_version_for_ssh(self):
        """IP version used for SSH connections."""
        return int(self.get("ip_version_for_ssh", 4))

    @property
    def catalog_type(self):
        """Catalog type of the Compute service."""
        return self.get("catalog_type", 'compute')

    @property
    def log_level(self):
        """Level for logging compute API calls."""
        return self.get("log_level", 'ERROR')


class ComputeAdminConfig(BaseConfig):

    SECTION_NAME = "compute-admin"

    @property
    def username(self):
        """Administrative Username to use for Nova API requests."""
        return self.get("username", "admin")

    @property
    def tenant_name(self):
        """Administrative Tenant name to use for Nova API requests."""
        return self.get("tenant_name", "admin")

    @property
    def password(self):
        """API key to use when authenticating as admin."""
        return self.get("password", "pass")


class ImagesConfig(BaseConfig):

    """
    Provides configuration information for connecting to an
    OpenStack Images service.
    """

    SECTION_NAME = "image"

    @property
    def host(self):
        """Host IP for making Images API requests. Defaults to '127.0.0.1'."""
        return self.get("host", "127.0.0.1")

    @property
    def port(self):
        """Listen port of the Images service."""
        return int(self.get("port", "9292"))

    @property
    def api_version(self):
        """Version of the API"""
        return self.get("api_version", "1")

    @property
    def username(self):
        """Username to use for Images API requests. Defaults to 'demo'."""
        return self.get("username", "demo")

    @property
    def password(self):
        """Password for user"""
        return self.get("password", "pass")

    @property
    def tenant_name(self):
        """Tenant to use for Images API requests. Defaults to 'demo'."""
        return self.get("tenant_name", "demo")


class NetworkConfig(BaseConfig):
    """Provides configuration information for connecting to an OpenStack
    Network Service.
    """

    SECTION_NAME = "network"

    @property
    def catalog_type(self):
        """Catalog type of the Quantum service."""
        return self.get("catalog_type", 'network')

    @property
    def api_version(self):
        """Version of Quantum API"""
        return self.get("api_version", "v1.1")


class WhiteBoxConfig(BaseConfig):
    """Provides configuration information required by white-box tests to access
    OpenStack internals
    """

    SECTION_NAME = "whitebox"

    @property
    def openstack_deploy_mode(self):
        """
        Indicate how OpenStack services are deployed, whether using devstack
        or package installation, on multiple remote nodes or on the single
        localhost. Used by tests for running commands locally or remotely.
        Allowed values are 'devstack-local, 'devstack-remote',
        'package-multi'.
        """
        return self.get("openstack_deploy_mode", "devstack-local")

    @property
    def compute_db_uri(self):
        """Connection string to the database of Compute service"""
        return self.get("compute_db_uri")

    @property
    def glance_db_uri(self):
        """Connection string to the database of Image Service"""
        return self.get("glance_db_uri")

    @property
    def keystone_db_uri(self):
        """Connection string to the database of Identity Service"""
        return self.get("keystone_db_uri")

    @property
    def quantum_db_uri(self):
        """Connection string to the database of Network Service"""
        return self.get("quantum_db_uri")

    @property
    def compute_source_dir(self):
        """Path of nova source directory"""
        return self.get("compute_source_dir", "/opt/stack/nova")

    @property
    def compute_config_path(self):
        """Path of nova configuration file"""
        return self.get("compute_config_path", "/etc/nova/nova.conf")

    @property
    def compute_bin_dir(self):
        """Directory containing nova binaries such as nova-manage"""
        return self.get("compute_binary_dir", "/usr/local/bin/")

    @property
    def path_to_private_key(self):
        """Path to a private key file for SSH access to remote hosts"""
        return self.get("path_to_private_key")


# TODO(jaypipes): Move this to a common utils (not data_utils...)
def singleton(cls):
    """Simple wrapper for classes that should only have a single instance"""
    instances = {}

    def getinstance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]
    return getinstance


@singleton
class TempestConfig:
    """Provides OpenStack configuration information."""

    DEFAULT_CONFIG_DIR = os.path.join(
        os.path.abspath(
          os.path.dirname(
            os.path.dirname(__file__))),
        "etc")

    DEFAULT_CONFIG_FILE = "tempest.conf"

    def __init__(self):
        """Initialize a configuration from a conf directory and conf file."""

        # Environment variables override defaults...
        conf_dir = os.environ.get('TEMPEST_CONFIG_DIR',
            self.DEFAULT_CONFIG_DIR)
        conf_file = os.environ.get('TEMPEST_CONFIG',
            self.DEFAULT_CONFIG_FILE)

        path = os.path.join(conf_dir, conf_file)

        LOG.info("Using tempest config file %s" % path)

        if not os.path.exists(path):
            msg = "Config file %(path)s not found" % locals()
            raise RuntimeError(msg)

        self._conf = self.load_config(path)
        self.compute = ComputeConfig(self._conf)
        self.compute_admin = ComputeAdminConfig(self._conf)
        self.identity = IdentityConfig(self._conf)
        self.identity_admin = IdentityAdminConfig(self._conf)
        self.images = ImagesConfig(self._conf)
        self.network = NetworkConfig(self._conf)
        self.whitebox = WhiteBoxConfig(self._conf)

    def load_config(self, path):
        """Read configuration from given path and return a config object."""
        config = ConfigParser.SafeConfigParser()
        config.read(path)
        return config
