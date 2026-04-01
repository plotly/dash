import sys

collect_ignore_glob = []

if sys.version_info < (3, 10):
    collect_ignore_glob.append("*")
