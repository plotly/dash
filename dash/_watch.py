import collections
import os
import re
import time


def watch(folders, on_change, pattern=None, sleep_time=0.1):
    pattern = re.compile(pattern) if pattern else None
    watched = collections.defaultdict(lambda: -1)

    def walk():
        for folder in folders:
            for current, _, files, in os.walk(folder):
                for f in files:
                    if pattern and not pattern.search(f):
                        continue
                    path = os.path.join(current, f)
                    info = os.stat(path)
                    new_time = info.st_mtime
                    if new_time > watched[path] > 0:
                        on_change(path)
                    watched[path] = new_time

    while True:
        walk()
        time.sleep(sleep_time)
