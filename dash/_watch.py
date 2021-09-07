import collections
import os
import re
import time
from typing import List, Callable, DefaultDict


def watch(
    folders: List[str],
    on_change: Callable,
    pattern: str = None,
    sleep_time: float = 0.1,
) -> None:
    compiled_pattern = re.compile(pattern) if pattern else None
    watched: DefaultDict[str, float] = collections.defaultdict(lambda: -1)

    def walk() -> None:
        walked = []
        for folder in folders:
            for current, _, files in os.walk(folder):
                for f in files:
                    if compiled_pattern and not compiled_pattern.search(f):
                        continue
                    path = os.path.join(current, f)

                    info = os.stat(path)
                    new_time = info.st_mtime

                    if new_time > watched[path] > 0:
                        on_change(path, new_time, False)

                    watched[path] = new_time
                    walked.append(path)

        # Look for deleted files
        for w in [x for x in watched.keys() if x not in walked]:
            del watched[w]
            on_change(w, -1, True)

    while True:
        walk()
        time.sleep(sleep_time)
