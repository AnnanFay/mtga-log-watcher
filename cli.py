#!/usr/bin/env python3.7
import sys
from subprocess import Popen, DETACHED_PROCESS
from mtga_log_watcher import watch, is_process_running


def spawn():
    cmdline = [sys.executable, __file__, "--watch"]
    # cmdline = sys.argv + ['--watch']
    existing = is_process_running(lambda p: cmdline == p.cmdline())

    if existing:
        print("found existing", existing)
        return

    print("spawning", cmdline)

    return Popen(cmdline, creationflags=DETACHED_PROCESS)


def main():
    print("sys.argv", sys.argv)

    if sys.argv[-1] == "--watch":
        watch()
    else:
        spawn()


if __name__ == "__main__":
    main()
