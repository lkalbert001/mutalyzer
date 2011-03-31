#!/usr/bin/python

"""
@requires: os
@requires: sys
@requires: daemon
@requires: signal
@requires: fcntl
@requires: ftplib
@requires: Modules.Config
@requires: Modules.Db.Batch
@requires: Modules.Scheduler
"""
import os
import sys
import daemon
import signal
import fcntl
import site

# Todo: Get this from the configuration file
root_dir = os.path.split(os.path.dirname(__file__))[0]
site.addsitedir(root_dir)
# Todo: Fix Mutalyzer to not depend on working directory
if not __name__ == '__main__':
    os.chdir(root_dir)

from mutalyzer.config import Config
from mutalyzer.Db import Batch
from mutalyzer import Scheduler

def sigusr1_daemon_notified(*args):
    """
    Stop the Daemon with SIGUSR1 signal: kill -10 PID
    """
    sys.exit()

# Change dir
#if len(sys.argv[0].split('/')) > 2 :
#    os.chdir(sys.argv[0].rsplit('/', 2)[0])

C = Config()

batchconfig = C.Batch
cwd = os.getcwd()
pidfile_path = os.path.realpath(batchconfig.PIDfile)

pidfile = open(pidfile_path, 'w')

try:
    fcntl.flock(pidfile.fileno(), fcntl.LOCK_EX|fcntl.LOCK_NB)
except IOError,e:
    #process is already running and file is locked
    print "Can't lock: %s\nBatchChecker already running\n" % pidfile_path
    sys.exit(2)

#If we get here the file is not locked and no Daemon is running.

# Write PID to pidfile
pidfile.write(`os.getpid()`)

# Populate signal map
sigmap ={signal.SIGUSR1: sigusr1_daemon_notified}
stdout = sys.stdout
DaemonInst = daemon.DaemonContext(signal_map = sigmap,
                files_preserve = [ pidfile ], working_directory = cwd)
DaemonInst.__enter__()
# stdout = stdout, stderr = stdout
C = Config()
D = Batch(C.Db)
S = Scheduler.Scheduler(C.Scheduler, D)
S.process()
DaemonInst.__exit__()
