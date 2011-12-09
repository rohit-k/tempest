import ConfigParser


class NodeObject(object):
    def __init__(self, value):
        self._set_node_info(value)

    def _set_node_info(self, value):
        node_info = value.split(':')
        self.ip = node_info[0]
        self.user = node_info[1]
        self.password = node_info[2]


class NodesConfig(object):
    """Provides configuration information for connecting to Nova."""

    def __init__(self, conf):
        """Initialize a Node-specific configuration object"""
        self.conf = conf

    def get(self, item_name, default_value=None):
        """Gets the value of specified config parameter"""
        try:
            return self.conf.get("nodes", item_name)
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
            return default_value

    @property
    def api(self):
        return self.get_node_list("api")

    @property
    def compute(self):
        return self.get_node_list("compute")

    @property
    def network(self):
        return self.get_node_list("network")

    @property
    def volume(self):
        return self.get_node_list("volume")

    @property
    def glance(self):
        return self.get_node_list("glance")

    @property
    def swift(self):
        return self.get_node_list("swift")

    @property
    def mysql(self):
        return self.get_node_list("mysql")

    @property
    def rabbitmq(self):
        return self.get_node_list("rabbitmq")

    @property
    def ssh_timeout(self):
        return self.get("ssh_timeout")

    def get_node_list(self, service):
        """Returns a list of node objects"""

        nodes = []
        node_val_list = self.get(service).split(',')
        for value in node_val_list:
            nodes.append(NodeObject(value))

        if len(nodes) <= 1:
            return nodes[0]
        return nodes

    def load_config(self, path=None):
        """Read configuration from given path and return a config object."""
        config = ConfigParser.SafeConfigParser()
        config.read(path)
        return config


class HavocConfig(object):
    """Provides OpenStack multi-node configuration"""

    def __init__(self, path=None):
        """Initialize a configuration from a path."""
        self._conf = self.load_config(self._path)
        self.nodes = NodesConfig(self._conf)

    def load_config(self, path=None):
        """Read configuration from given path and return a config object."""
        config = ConfigParser.SafeConfigParser()
        config.read(path)
        return config
