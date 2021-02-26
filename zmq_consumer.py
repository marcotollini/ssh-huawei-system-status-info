import zmq
import argparse
import curses
from curses import wrapper
from functools import partial


class Printer:
    def __init__(self):
        self.in_place = False

    def start_in_place(self, stdscr):
        self.stdscr = stdscr
        self.print_mem = {}
        self.in_place = True
        stdscr.clear()

    def pad(self, word, dimension):
        return word + ' ' * max(dimension - len(word), 0)

    def to_console(self, ip, info):
        print(f'------ {ip} -----')
        for process in info:
            cpu = info[process][0]
            mem = info[process][1]
            proc_col = self.pad(f'{process}:', 15)
            cpu_col = self.pad(f'{cpu}%', 8)
            mem_col = mem

            print(f'{proc_col}{cpu_col}{mem_col}')

    def to_replace(self, ip, info):
        self.print_mem[ip] = info

        try:
            i = 0
            for ip in self.print_mem:
                self.stdscr.addstr(i, 0, f'----- {ip} -----')
                i += 1
                ip_info = self.print_mem[ip]
                for process in info:
                    cpu = ip_info[process][0]
                    mem = ip_info[process][1]
                    proc_col = self.pad(f'{process}:', 15)
                    cpu_col = self.pad(f'{cpu}%', 8)
                    mem_col = mem

                    self.stdscr.addstr(i, 0, f'{proc_col}{cpu_col}{mem_col}')
                    i += 1
        except curses.error:
            pass
        self.stdscr.refresh()

    def print(self, ip, cpu, memory):
        cpu_dict = {x[0]: x[1] for x in cpu}
        memory_dict = {x[1]: x[2] for x in memory}
        processes = set([*cpu_dict.keys(), *memory_dict.keys()])
        info = {x: [cpu_dict.get(x), memory_dict.get(x)] for x in processes}

        if not self.in_place:
            self.to_console(ip, info)
        else:
            self.to_replace(ip, info)


def main(args, stdscr = None):
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.bind("tcp://*:5678")
    socket.setsockopt_string(zmq.SUBSCRIBE, '')

    printer = Printer()
    if stdscr is not None:
        printer.start_in_place(stdscr)

    while True:
        data = socket.recv_pyobj()
        ip = data['ip']
        cpu = data['cpu']
        memory = data['memory']
        if args.processes is not None:
            cpu = [x for x in cpu if x[0] in args.processes]
            memory = [x for x in memory if x[1] in args.processes]

        printer.print(ip, cpu, memory)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Read and parse system status informations for a good output')

    parser.add_argument('-z', '--zmq', dest='zmq', required=True,
                        help='ZMQ Server and port as tcp://*:5678')

    parser.add_argument('-s', '--standard', dest='standard', action='store_const',
                        const=True, default=False, help='In place: rewrite the output. Standard: use normal print')

    parser.add_argument('-p', '--process', dest='processes', required=False, action='append',
                        help='List of processes you want to see. Use -p multiple times')


    args = parser.parse_args()

    m = partial(main, args)
    if not args.standard:
        wrapper(m)
    else:
        m()
