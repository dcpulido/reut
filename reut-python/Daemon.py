#!/usr/bin/python
import time
from daemon import runner


class Daemon():
    def __init__(self,
                 conf):
        self.conf = conf
        self.stdin_path = conf["stdin_path"]
        self.stdout_path = conf["stdout_path"]
        self.stderr_path = conf["stderr_path"]
        self.pidfile_path = conf["pidfile_path"]
        self.pidfile_timeout = conf["pidfile_timeout"]

    def run(self):
        while True:
            print("Howdy!  Gig'em!  Whoop!")
            time.sleep(10)


cconf = dict(stdin_path='/dev/null',
             stdout_path='/dev/tty',
             stderr_path='/dev/tty',
             pidfile_path='/tmp/foo.pid',
             pidfile_timeout=5)
app = Daemon(cconf)
daemon_runner = runner.DaemonRunner(app)
daemon_runner.do_action()
