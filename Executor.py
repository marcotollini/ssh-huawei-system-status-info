import paramiko
import logging
import json
from time import sleep

class Executor:
    def __init__(self, router_config, should_print_console):
        self.ip = router_config['mgmt_ip']
        self.user = router_config['user']
        self.password = router_config['password']
        self.frequency = router_config['frequency']
        self.append = router_config['append']
        self.should_print_console = should_print_console

        self.logger = logging.getLogger(self.ip)

        self.logger.debug('Opening ssh connection')
        self.ssh = paramiko.SSHClient()
        self.ssh.get_transport().set_keepalive(60)
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect(self.ip, username=self.user, password=self.password)
        self.logger.info('SSH connection opened')

        self.should_stop = False

        self.command_cpu = 'display cpu-usage slot 3'
        self.command_memory = 'display memory-usage slot 3'

    def start(self):
        while(not self.should_stop):
            try:
                ssh_stdin, ssh_stdout, ssh_stderr = self.ssh.exec_command(self.command_cpu, get_pty=True)
                print(ssh_stdout)
            except:
                self.logger.error('Error happened while running a command', exc_info=True)
