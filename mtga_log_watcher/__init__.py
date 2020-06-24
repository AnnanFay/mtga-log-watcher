#!/usr/bin/env python3.7
import re
import os
import sys
from pystray import Icon, Menu, MenuItem
from plyer import notification
from PIL import Image
import humanize
from time import sleep
from threading import Thread
from datetime import date, datetime
import traceback
import errno
import shutil
from psutil import process_iter, NoSuchProcess, AccessDenied, ZombieProcess

try:
    import importlib.resources as pkg_resources
except ImportError:
    import importlib_resources as pkg_resources

from . import assets

"""
Simple log update background script.
Requires : psutil plyer

When run without arguments will spawn a background process which watching
the `Player.log` and tries to back it up

Currently the background process must be manually killed through task 
manager or kill commands.

Run with --watch to run in foreground.

"""

LOG_DIR = os.path.expandvars(r"%APPDATA%\..\LocalLow\Wizards Of The Coast\MTGA")
WATCH_LOG = os.path.join(LOG_DIR, "Player.log")
TARGET_DIR = os.path.join(LOG_DIR, "./named_logs")
WATCHER_LOG = os.path.join(LOG_DIR, "log_watcher.log")
WATCHER_ERR_LOG = os.path.join(LOG_DIR, "log_watcher.err")

FAIL_LIMIT = 10
BIG_LOG_SIZE = 32 * 1024 * 1024
ICON_PATH = "icon.png"

# FIXME: Find a better way
TERMINATE = False

print("using python:", sys.version)


def notify(message):
    try:
        notification.notify(
            title="MTGA Log Watcher", message=message, app_name="MTGA Log Watcher"
        )
    except:
        print('Notify failed.')


def log_error(err):
    print("logging failures")

    with open(WATCHER_ERR_LOG, "a") as el:
        el.write("""{}""".format(traceback.format_exc()))

    notify(
        "Could not backup log after {} retires. Terminating. Error: {}".format(
            FAIL_LIMIT, err
        )
    )


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def backup(filename, force=False):
    mtimestamp = os.path.getmtime(filename)
    mdatetime = datetime.fromtimestamp(mtimestamp)
    mstring = mdatetime.strftime("%Y-%m-%d_%H-%M-%S")

    basename = os.path.basename(filename)
    new_filename = "{}/{}_{}".format(TARGET_DIR, mstring, basename)

    # check if file already exists, and has the same size.
    # if it does then we don't need to backup

    if not force and os.path.exists(new_filename):
        from_size = os.path.getsize(filename)
        to_size = os.path.getsize(new_filename)
        if from_size == to_size:
            # we don't need to do anything
            return

        # otherwise they are different in size,
        # but we cannot overwrite.
        raise Error("Cannot rename, file exists but is different")

    print("backup")
    print("    FROM :", filename)
    print("    TO   :", new_filename)

    mkdir_p(TARGET_DIR)

    try:
        # Rename might fail if a tracker has a file lock
        rename(filename, new_filename)
    except:
        shutil.copyfile(filename, new_filename)


def rename(a, b):
    if not os.path.exists(b):
        os.rename(a, b)
    else:
        raise Error("Cannot rename, file exists")


def check_log_exists():
    return os.path.exists(WATCH_LOG)


def get_arena():
    return is_process_running(lambda p: "MTGA.exe" == p.name())


def get_log_size():
    if check_log_exists():
        return os.path.getsize(WATCH_LOG)


def get_log_created():
    if check_log_exists():
        ctimestamp = os.path.getctime(WATCH_LOG)
        cdate = datetime.fromtimestamp(ctimestamp)
        return cdate


LAST_BACKUP = False


def monitor_log(icon):
    global LAST_BACKUP
    print("Watching")
    big_log_notified = False

    backup_failures = 0
    while not TERMINATE:

        icon.update_menu()

        sleep(2.0)  # seconds

        arena_proc = get_arena()

        with open(WATCHER_LOG, "w") as wl:
            wl.write("{}{}{}".format("arena_proc: ", arena_proc, "\n"))
            wl.write("{}{}{}".format("watch log: ", WATCH_LOG, "\n"))
            wl.write("{}{}{}".format("check_log_exists: ", check_log_exists(), "\n"))
            wl.write("{}{}{}".format("get_log_size: ", get_log_size(), "\n"))

        if get_log_size():
            if not big_log_notified and get_log_size() > BIG_LOG_SIZE:
                # only notify once.
                notify(
                    "Log, is like, really big: ".format(
                        humanize.naturalsize(get_log_size(), binary=True)
                    )
                )
                big_log_notified = True

        log_exists = check_log_exists()

        if log_exists:
            print("Log Size:", humanize.naturalsize(get_log_size(), binary=True))
        else:
            print(".", end="", flush=True)

        if arena_proc:
            if log_exists:
                # wait until arena closes
                pass
            else:
                # wait until log exists
                pass
        else:
            if log_exists:
                # when the log exists but arena is closed,
                # we backup()
                try:
                    backup(WATCH_LOG)
                    backup_failures = 0
                    LAST_BACKUP = datetime.now()

                except Exception as e:
                    # if backup fails we pass and
                    # retry next loop
                    backup_failures += 1
                    print("backup failure:", backup_failures)

                    if backup_failures > FAIL_LIMIT:
                        # exit and notify
                        log_error(e)
                        raise e
            else:
                # wait until arena makes log file
                pass

    print("Watcher: Stopping")


def watch():
    def noop(icon, item):
        pass

    def quit(icon, item):
        global TERMINATE
        print("Watcher: Marking")
        TERMINATE = True
        watcher.join()

        print("Icon: Stopping")
        icon.stop()

    def last_log_backup_text(arg):
        if LAST_BACKUP:
            htdelta = humanize.naturaldelta(LAST_BACKUP - datetime.now())
            return "Last Backup: {}".format(htdelta)
        else:
            return "Last Backup: Unknown"

    def log_age_text(arg):
        if get_log_size():
            cdate = get_log_created()
            tdelta = cdate - datetime.now()
            return "Log age : {}".format(humanize.naturaldelta(tdelta))
        else:
            return "Log age : N/A"

    def get_log_size_text(arg):
        log_size = get_log_size()
        if log_size:
            size = humanize.naturalsize(log_size, binary=True)
            return "Log Size: {}".format(size)
        else:
            return "Log Size: N/A"

    def arena_status_text(arg):
        if get_arena():
            return "Arena is on!"
        else:
            return "[Start Arena]"

    menu = Menu(
        MenuItem("Quit", quit, default=True),
        MenuItem(arena_status_text, noop, enabled=lambda x: not get_arena()),
        MenuItem(get_log_size_text, noop, enabled=False),
        MenuItem(log_age_text, noop, enabled=False),
        MenuItem(last_log_backup_text, noop, enabled=False),
    )

    icon_image = Image.open(pkg_resources.open_binary(assets, ICON_PATH))

    icon = Icon(
        name="MTGA Log Watcher Icon",
        icon=icon_image,
        title="MTGA Log Watcher",
        menu=menu,
    )

    watcher = Thread(target=monitor_log, args=(icon,))
    watcher.start()
    icon.run()
    print("Exiting")


def is_process_running(pred):
    for proc in process_iter():
        try:
            if pred(proc):
                return proc
        except (NoSuchProcess, AccessDenied, ZombieProcess, OSError):
            pass
    return False
