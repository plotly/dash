"""Runs inside a replica: talks to the app on loopback and prints JSON.

    probe.py get /path            one request
    probe.py post /path '{json}' [timeout]  one request
    probe.py workers /path N secs  repeat until N gunicorn workers answered
"""
import json
import sys
import time
import urllib.error
import urllib.request

BASE = "http://127.0.0.1:8050"


def call(method, path, body=None, timeout=20):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(
        BASE + path,
        data=data,
        method=method,
        headers={"Content-Type": "application/json", "Connection": "close"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as res:
            return {"status": res.status, "body": json.loads(res.read())}
    except urllib.error.HTTPError as err:
        return {"status": err.code, "body": None}
    except Exception as err:  # pylint: disable=broad-except
        return {"status": 0, "error": f"{type(err).__name__}: {err}"}


def main():
    cmd, path = sys.argv[1], sys.argv[2]
    if cmd == "get":
        out = call("GET", path)
    elif cmd == "post":
        timeout = float(sys.argv[4]) if len(sys.argv) > 4 else 20
        out = call("POST", path, json.loads(sys.argv[3]), timeout)
    else:
        # A worker can be busy for a while (a call to an owner that vanished),
        # so keep asking for a time, not a number of requests.
        workers, deadline = int(sys.argv[3]), time.monotonic() + float(sys.argv[4])
        out = {}
        while time.monotonic() < deadline:
            res = call("GET", path)
            if res["status"] != 200:
                out = {"error": res}
                break
            out[str(res["body"]["pid"])] = res["body"]
            if len(out) >= workers:
                break
            time.sleep(0.05)
    print(json.dumps(out))


main()
