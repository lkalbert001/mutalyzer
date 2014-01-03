"""
Mutalyzer batch processor.

.. todo: Get rid of ugly exception logging.
.. todo: Reload configuration without restarting (for example, on SIGHUP).
"""


import argparse
import signal
import sys
import time

from .. import config
from .. import Db
from .. import Scheduler


def process():
    """
    Run forever in a loop processing scheduled batch jobs.
    """
    counter = Db.Counter()
    scheduler = Scheduler.Scheduler()

    def handle_exit(signum, stack_frame):
        if scheduler.stopped():
            sys.stderr.write('mutalyzer-batchd: Terminated\n')
            sys.exit(1)
        if signum == signal.SIGINT:
            sys.stderr.write('mutalyzer-batchd: Hitting Ctrl+C again will '
                             'terminate any running job!\n')
        scheduler.stop()

    signal.signal(signal.SIGTERM, handle_exit)
    signal.signal(signal.SIGINT, handle_exit)

    while True:
        # Process batch jobs.
        scheduler.process(counter)
        if scheduler.stopped():
            break
        # Wait a bit and process any possible new jobs.
        time.sleep(1)

    sys.stderr.write('mutalyzer-batchd: Graceful shutdown\n')
    sys.exit(0)


def main():
    """
    Command line interface to the batch processor.
    """
    parser = argparse.ArgumentParser(
        description='Mutalyzer batch processor.',
        epilog='The process can be shutdown gracefully by sending a SIGINT '
        '(Ctrl+C) or SIGTERM signal.')

    parser.parse_args()
    process()


if __name__ == '__main__':
    main()