import os
import sys
import unicodedata

from subprocess import Popen as _Popen, PIPE as _PIPE


def _which_dirs(cmd):
    result = set()
    for path in os.environ.get('PATH', '').split(os.pathsep):
        filename = os.path.join(path, cmd)
        if os.access(filename, os.X_OK):
            result.add(path)
    return result


def run_setup_py(cmd, pypath=None, path=None,
                 data_stream=0, env=None):
    """
    Execution command for tests, separate from those used by the
    code directly to prevent accidental behavior issues
    """
    if env is None:
        env = dict()
        for envname in os.environ:
            env[envname] = os.environ[envname]

    #override the python path if needed
    if pypath is not None:
        env["PYTHONPATH"] = pypath

    #overide the execution path if needed
    if path is not None:
        env["PATH"] = path
    if not env.get("PATH", ""):
        env["PATH"] = _which_dirs("tar").union(_which_dirs("gzip"))
        env["PATH"] = os.pathsep.join(env["PATH"])

    cmd = [sys.executable, "setup.py"] + list(cmd)

    # http://bugs.python.org/issue8557
    shell = sys.platform == 'win32'

    try:
        proc = _Popen(
            cmd, stdout=_PIPE, stderr=_PIPE, shell=shell, env=env,
        )

        data = proc.communicate()[data_stream]
    except OSError:
        return 1, ''

    #decode the console string if needed
    if hasattr(data,  "decode"):
        # use the default encoding
        data = data.decode()
        data = unicodedata.normalize('NFC', data)

    #communciate calls wait()
    return proc.returncode, data
