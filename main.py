import argparse
import json
import logging
import threading

from Executor import Executor

def setup_logging(debug):
    logger = logging.getLogger()
    if not debug:
        logger.setLevel(logging.INFO)
    else:
        logger.setLevel(logging.DEBUG)
    c_handler = logging.StreamHandler()
    c_format = logging.Formatter(
        '[%(asctime)s] %(levelname)s - %(name)s - %(message)s')
    c_handler.setFormatter(c_format)
    logger.addHandler(c_handler)


def main():
    parser = argparse.ArgumentParser(
        description='Save the processes status of Huawei routers on a file')

    parser.add_argument('-d', '--debug', dest='debug', action='store_const',
                        const=True, default=False, help='Debug mode')
    parser.add_argument('-p', '--console', dest='console', action='store_const',
                        const=True, default=False, help='Write the state also on the console')

    parser.add_argument('-c', '--config', dest='config_path', required=True,
                        help='Configuration file')

    parser.add_argument('-z', '--zmq', dest='zmq', required=False,
                        help='ZMQ Server and port as tcp://localhost:4567')


    args = parser.parse_args()

    setup_logging(args.debug)

    with open(args.config_path, 'r') as config_fp:
        config = json.load(config_fp)
    logging.info(f'config file correctly loaded with {len(config)} routers')

    if args.zmq is not None:
        logging.info('ZMQ is enabled')

    executors = []
    threads = []
    for router in config:
        executor = Executor(router, args.console, args.zmq)
        thread = threading.Thread(target=executor.start)
        executors.append(executor)
        threads.append(thread)

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

if __name__ == "__main__":
    main()

    # text = '---\n' + text
    # rows = text.split('\n')
    # sections_indexes = [i for i in range(len(rows)) if '---' in rows[i]]
    # sections = [rows[sections_indexes[si]+1 : sections_indexes[si+1]] for si in range(len(sections_indexes) - 1)]

    # interesting_section = sections[3]
    # print(interesting_section)
    # splitting = [r.split(' ') for r in interesting_section]
    # splitting_cleaned = [[y for y in x if y != ''] for x in splitting]
    # # processes = [[' '.join(p[:-1]), int(p[-1][:-1])] for p in splitting_cleaned]
    # processes = [[p[0], ' '.join(p[1:-1]), int(p[-1])] for p in splitting_cleaned]
    # print(processes)
