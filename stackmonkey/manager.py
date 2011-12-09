import sys
import subprocess
import config
import exception
from time import sleep
from tempest.common import ssh


class HavocManager(object):
    """Manager Base Class for Havoc actions"""

    DEFAULT_CONFIG_DIR = os.path.join(
        os.path.abspath(
          os.path.dirname(
            os.path.dirname(__file__))),
        "etc")
    DEFAULT_CONFIG_FILE = "havoc.conf"

    def __init__(self):
        config_dir = os.environ.get('HAVOC_CONFIG_DIR',
            self.DEFAULT_CONFIG_DIR)
        config_file = os.environ.get('HAVOC_CONFIG',
            self.DEFAULT_CONFIG_FILE)
        self.config = config.HavocConfig()
        self.nodes = self.config.nodes
        self.timeout = self.config.nodes.ssh_timeout

    def connect(self, host, username, password, timeout=None):
        """Create Connection object"""

        if timeout is None:
            timeout = self.timeout
        try:
            ssh_client = ssh.Client(host, username, password, timeout)
            return ssh_client
        except:
            raise

    def _run_cmd(self, client, command):
        """Execute remote shell command"""

        try:
            output = client.exec_command(command)
            exit_code = client.exec_command('echo $?')
            if exit_code:
                return output
        except:
            raise exception.SSHException

    def _is_service_running(self, client, service):
        """Checks if service is running"""

        command = 'service %s status' % service
        output = self._run_cmd(client, command)
        if 'start/running' in output:
            return True
        elif 'stop/waiting' in output:
            return False

    def _is_process_running(self, client, process):
        """Checks if a process is running"""

        process_check = '[%s]' % process[0] + process[1:]
        command = 'ps aux | grep %s' % process_check
        output = self._run_cmd(client, command).strip('\n')
        if process in output:
            return True
        return False

    def service_action(self, client, service, action):
        """Perform the requested action on a service on remote host"""

        if action == 'start':
            if self._is_service_running(client, service):
                return

        elif action in ('stop', 'restart', 'reload', 'force-reload'):
            if not self._is_service_running(client, service):
                return

        else:
            raise exception.HavocException

        command = 'service %s %s' % (service, action)
        return self._run_cmd(client, command)

    def process_action(self, client, process, action):
        if action == 'killall' and self._is_process_running(client, process):
            command = 'killall %s' % process
            self._run_cmd(client, command)
            return not self._is_process_running(client, process)

        if action == 'verify':
            return self._is_process_running(client, process)


class NetworkHavoc(HavocManager):
    """Class that performs Network node specific Havoc actions"""

    def __init__(self, host, username, password, timeout=None):
        super(NetworkHavoc, self).__init__()
        self.host = host
        self.username = username
        self.password = password
        self.network_service = 'nova-network'
        self.host = self.connect(self.host, self.username, self.password,
                                      self.timeout)

    def stop_nova_network(self):
        return self.service_action(self.host, self.network_service, 'stop')

    def start_nova_network(self):
        return self.service_action(self.host, self.network_service, 'start')

    def restart_nova_network(self):
        return self.service_action(self.host, self.network_service, 'restart')

    def kill_dnsmasq(self):
        return self.process_action(self.host, 'dnsmasq', 'killall')

    def start_dnsmasq(self):
        """Restarting nova-network would restart dnsmasq process"""

        self.service_action(self.host, self.network_service, 'restart')
        sleep(1)
        return self.process_action(self.host, 'dnsmasq', 'verify')


class ComputeHavoc(HavocManager):
    """Class that performs Compute node specific Havoc actions"""

    def __init__(self, host, username, password, timeout=None):
        super(ComputeHavoc, self).__init__()
        self.host = host
        self.username = username
        self.password = password
        self.compute_service = 'nova-compute'
        self.host = self.connect(self.host, self.username, self.password,
                                      self.timeout)

    def stop_nova_compute(self):
        return self.service_action(self.host, self.compute_service, 'stop')

    def start_nova_compute(self):
        return self.service_action(self.host, self.compute_service, 'start')

    def restart_nova_compute(self):
        return self.service_action(self.host, self.compute_service, 'restart')

    def stop_libvirt(self):
        return self.service_action(self.host, 'libvirt-bin', 'stop')

    def start_libvirt(self):
        return self.service_action(self.host, 'libvirt-bin', 'start')

    def restart_libvirt(self):
        return self.service_action(self.host, 'libvirt-bin', 'restart')


class PowerHavoc(HavocManager):
    """Class that performs Power Management Havoc actions"""

    def __init__(self, host, username, password, timeout=None):
        super(PowerHavoc, self).__init__()
        self.host = host
        self.username = username
        self.password = password
        self.ipmi_host = host
        self.ipmi_user = username
        self.ipmi_password = password
        self.power_cmd = None
        self.timeout = timeout

    def power_on(self):
        power_cmd = 'power on'
        power_on_msg = 'Chassis Power Control: Up/On'
        self.ipmi_cmd = 'ipmitool -I lan -H %s -U %s -P %s %s' % (
                                                           self.ipmi_host,
                                                           self.ipmi_user,
                                                           self.ipmi_password,
                                                           power_cmd)
        _PIPE = subprocess.PIPE
        self.ipmi_cmd_list = self.ipmi_cmd.split(" ")
        obj = subprocess.Popen(self.ipmi_cmd_list,
                               stdin=_PIPE,
                               stdout=_PIPE,
                               stderr=_PIPE,
                               )
        result = obj.communicate()
        return_status = result[0].strip()
        if power_off_status_msg in return_status:
            return True
        return False

    def power_off(self):
        power_cmd = 'power off'
        power_off_msg = 'Chassis Power Control: Down/Off'
        self.ipmi_cmd = 'ipmitool -I lan -H %s -U %s -P %s %s' % (
                                                           self.ipmi_host,
                                                           self.ipmi_user,
                                                           self.ipmi_password,
                                                           power_cmd)
        _PIPE = subprocess.PIPE
        self.ipmi_cmd_list = self.ipmi_cmd.split(" ")
        obj = subprocess.Popen(self.ipmi_cmd_list,
                               stdin=_PIPE,
                               stdout=_PIPE,
                               stderr=_PIPE,
                               )
        result = obj.communicate()
        return_status = result[0].strip()
        if power_off_msg in return_status:
            return True
        return False

    def is_power_on(self):
        power_cmd = 'power status'
        power_on_status_msg = 'Chassis Power is on'
        power_off_status_msg = 'Chassis Power is off'
        self.ipmi_cmd = 'ipmitool -I lan -H %s -U %s -P %s %s' % (
                                                           self.ipmi_host,
                                                           self.ipmi_user,
                                                           self.ipmi_password,
                                                           power_cmd)
        _PIPE = subprocess.PIPE
        self.ipmi_cmd_list = self.ipmi_cmd.split(" ")
        obj = subprocess.Popen(self.ipmi_cmd_list,
                               stdin=_PIPE,
                               stdout=_PIPE,
                               stderr=_PIPE,
                               )
        result = obj.communicate()
        return_status = result[0].strip()
        if power_on_status_msg in return_status:
            return True
        return False
