import paramiko
import logging
import json
from time import sleep, time
import socket
import zmq


class Executor:
    def __init__(self, router_config, should_print_console, zmq):
        self.ip = router_config['mgmt_ip']
        self.user = router_config['user']
        self.password = router_config['password']
        self.frequency = router_config['frequency']
        self.output = router_config.get('output')
        self.should_print_console = should_print_console
        self.zmq = zmq

        self.logger = logging.getLogger(self.ip)

        self.logger.debug('Opening ssh connection')
        self.ssh = paramiko.SSHClient()
        # self.ssh.get_transport().set_keepalive(60)
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect(self.ip, username=self.user, password=self.password)
        self.logger.info('SSH connection opened')

        self.should_stop = False

        self.command_cpu = 'display cpu-usage slot 3 | no-more\n'
        self.command_memory = 'display memory-usage slot 3 | no-more\n'

        self.channel = self.ssh.invoke_shell()

    def send_command(self, command):
        buffer = ''
        self.channel.send(command)

        while '<' not in buffer:
            buffer += self.channel.recv(10000).decode("utf-8")
        return buffer

    def connect_zqm(self):
        self.logger.info(f'Connecting to ZMQ: {self.zmq}')
        context = zmq.Context()
        self.zmq_socket = context.socket(zmq.PUB)
        self.zmq_socket.connect(self.zmq)


    def parse_cpu(self, ans):
        ans = '---\n' + ans
        rows = ans.split('\n')
        rows_cleaned = [x.strip() for x in rows]
        sections_indexes = [i for i in range(len(rows_cleaned)) if '---' in rows_cleaned[i]]
        sections = [rows_cleaned[sections_indexes[si]+1 : sections_indexes[si+1]] for si in range(len(sections_indexes) - 1)]

        interesting_section = sections[2]
        splitting = [r.split(' ') for r in interesting_section]
        splitting_cleaned = [[y for y in x if y != ''] for x in splitting]
        processes = [[' '.join(p[:-1]), int(p[-1][:-1])] for p in splitting_cleaned]
        return processes

    def run_cpu_command(self):
        self.logger.debug('Sending cpu command')
        ans = self.send_command(self.command_cpu)
        self.logger.debug('Cpu command received')
        programs = self.parse_cpu(ans)
        self.logger.debug('Cpu parsed correctly')
        return programs

    def parse_memory(self, ans):
        ans = '---\n' + ans
        rows = ans.split('\n')
        rows_cleaned = [x.strip() for x in rows]
        sections_indexes = [i for i in range(len(rows_cleaned)) if '---' in rows_cleaned[i]]
        sections = [rows_cleaned[sections_indexes[si]+1 : sections_indexes[si+1]] for si in range(len(sections_indexes) - 1)]

        interesting_section = sections[3]
        splitting = [r.split(' ') for r in interesting_section]
        splitting_cleaned = [[y for y in x if y != ''] for x in splitting]
        processes = [[p[0], ' '.join(p[1:-1]), int(p[-1])] for p in splitting_cleaned]
        return processes

    def run_memory_command(self):
        self.logger.debug('Sending memory command')
        ans = self.send_command(self.command_memory)
        self.logger.debug('memory command received')
        programs = self.parse_memory(ans)
        self.logger.debug('memory parsed correctly')
        return programs

    def append_info(self, cpu, memory):
        self.logger.debug('Sending to file')
        value = {
            'ip': self.ip,
            'freq': self.frequency,
            'cpu': cpu,
            'memory': memory
        }
        with open(self.output, 'a+') as fp:
            fp.write(json.dumps(value))
            fp.write('\n')

    def print_console(self, cpu, memory):
        self.logger.debug('Sending to console')
        cpu_arr = [f'{x[0]}: {x[1]}' for x in cpu]
        memory_arr = [f'({x[0]}) {x[1]}: {x[2]}' for x in memory]
        self.logger.info(f'ip: {self.ip} - freq: {self.frequency} - cpu: {", ".join(cpu_arr)} - memory: {", ".join(memory_arr)}')

    def send_zmq(self, cpu, memory):
        self.logger.debug('Sending to ZMQ')

        value = {
            'ip': self.ip,
            'freq': self.frequency,
            'cpu': cpu,
            'memory': memory
        }
        self.zmq_socket.send_pyobj(value)


    def start(self):
        if self.zmq:
            self.connect_zqm()

        sleep(3)
        self.channel.recv(10000)

        while not self.should_stop:
            start_iteration = time()

            cpu = self.run_cpu_command()
            memory = self.run_memory_command()

            if self.output:
                self.append_info(cpu, memory)

            if self.should_print_console:
                self.print_console(cpu, memory)

            if self.zmq:
                self.send_zmq(cpu, memory)


            end_iteration = time()
            sleep_time = self.frequency - (end_iteration - start_iteration)
            self.logger.debug(f'waiting for {sleep_time}s')
            if sleep_time < 0:
                self.logger.warning('Can\'t keep up. The frequency is too high. Best effort mode.')
            sleep(max(0, sleep_time))






