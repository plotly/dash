import sys
import tarfile
import contextlib

def _tarfile_open_ex(*args, **kwargs):
	"""
	Extend result as a context manager.
	"""
	return contextlib.closing(tarfile.open(*args, **kwargs))

if sys.version_info[:2] < (2, 7) or (3, 0) <= sys.version_info[:2] < (3, 2):
    tarfile_open = _tarfile_open_ex
else:
    tarfile_open = tarfile.open
