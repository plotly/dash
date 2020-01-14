# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import shlex
import sys
import uuid
import hashlib
import collections
import subprocess
import logging
from io import open  # pylint: disable=redefined-builtin
from functools import wraps
import future.utils as utils
from . import exceptions

logger = logging.getLogger()


def interpolate_str(template, **data):
    s = template
    for k, v in data.items():
        key = "{%" + k + "%}"
        s = s.replace(key, v)
    return s


def format_tag(tag_name, attributes, inner="", closed=False, opened=False):
    tag = "<{tag} {attributes}"
    if closed:
        tag += "/>"
    elif opened:
        tag += ">"
    else:
        tag += ">" + inner + "</{tag}>"
    return tag.format(
        tag=tag_name,
        attributes=" ".join(
            ['{}="{}"'.format(k, v) for k, v in attributes.items()]
        ),
    )


def generate_hash():
    return str(uuid.uuid4().hex).strip("-")


def get_asset_path(requests_pathname, asset_path, asset_url_path):

    return "/".join(
        [
            # Only take the first part of the pathname
            requests_pathname.rstrip("/"),
            asset_url_path,
            asset_path,
        ]
    )


def get_relative_path(requests_pathname, path):
    if requests_pathname == '/' and path == '':
        return '/'
    elif requests_pathname != '/' and path == '':
        return requests_pathname
    elif not path.startswith('/'):
        raise exceptions.UnsupportedRelativePath(
            "Paths that aren't prefixed with a leading / are not supported.\n" +
            "You supplied: {}".format(path)
        )
    return "/".join(
        [
            requests_pathname.rstrip("/"),
            path.lstrip("/")
        ]
    )

def strip_relative_path(requests_pathname, path):
    if path is None:
        return None
    elif ((requests_pathname != '/' and
            not path.startswith(requests_pathname.rstrip('/')))
            or (requests_pathname == '/' and not path.startswith('/'))):
        raise exceptions.UnsupportedRelativePath(
            "Paths that aren't prefixed with a leading " +
            "requests_pathname_prefix are not supported.\n" +
            "You supplied: {} and requests_pathname_prefix was {}".format(
                path,
                requests_pathname
            )
        )
    if (requests_pathname != '/' and
            path.startswith(requests_pathname.rstrip('/'))):
        path = path.replace(
            # handle the case where the path might be `/my-dash-app`
            # but the requests_pathname_prefix is `/my-dash-app/`
            requests_pathname.rstrip('/'),
            '',
            1
        )
    return path.strip('/')


# pylint: disable=no-member
def patch_collections_abc(member):
    return getattr(collections if utils.PY2 else collections.abc, member)


class AttributeDict(dict):
    """Dictionary subclass enabling attribute lookup/assignment of keys/values.

    For example::
        >>> m = AttributeDict({'foo': 'bar'})
        >>> m.foo
        'bar'
        >>> m.foo = 'not bar'
        >>> m['foo']
        'not bar'
    ``AttributeDict`` objects also provide ``.first()`` which acts like
    ``.get()`` but accepts multiple keys as arguments, and returns the value of
    the first hit, e.g.::
        >>> m = AttributeDict({'foo': 'bar', 'biz': 'baz'})
        >>> m.first('wrong', 'incorrect', 'foo', 'biz')
        'bar'
    """

    def __setattr__(self, key, value):
        self[key] = value

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            pass
        # to conform with __getattr__ spec
        # but get out of the except block so it doesn't look like a nested err
        raise AttributeError(key)

    def set_read_only(self, names, msg="Attribute is read-only"):
        object.__setattr__(self, "_read_only", names)
        object.__setattr__(self, "_read_only_msg", msg)

    def finalize(self, msg="Object is final: No new keys may be added."):
        """Prevent any new keys being set."""
        object.__setattr__(self, "_final", msg)

    def __setitem__(self, key, val):
        if key in self.__dict__.get("_read_only", []):
            raise AttributeError(self._read_only_msg, key)

        final_msg = self.__dict__.get("_final")
        if final_msg and key not in self:
            raise AttributeError(final_msg, key)

        return super(AttributeDict, self).__setitem__(key, val)

    # pylint: disable=inconsistent-return-statements
    def first(self, *names):
        for name in names:
            value = self.get(name)
            if value:
                return value


def create_callback_id(output):
    if isinstance(output, (list, tuple)):
        return "..{}..".format(
            "...".join(
                "{}.{}".format(x.component_id, x.component_property)
                for x in output
            )
        )

    return "{}.{}".format(output.component_id, output.component_property)


def run_command_with_process(cmd):
    is_win = sys.platform == "win32"
    proc = subprocess.Popen(shlex.split(cmd, posix=is_win), shell=is_win)
    proc.wait()
    if proc.poll() is None:
        logger.warning("🚨 trying to terminate subprocess in safe way")
        try:
            proc.communicate()
        except Exception:  # pylint: disable=broad-except
            logger.exception("🚨 first try communicate failed")
            proc.kill()
            proc.communicate()


def compute_md5(path):
    with open(path, encoding="utf-8") as fp:
        return hashlib.md5(fp.read().encode("utf-8")).hexdigest()


def job(msg=""):
    def wrapper(func):
        @wraps(func)
        def _wrapper(*args, **kwargs):
            logger.info("🏗️  [%s] 🏗️️  - %s", func.__name__, msg)
            res = func(*args, **kwargs)
            logger.info("::: 🍻🍻🍻 [%s] job done 🍻🍻🍻 :::", func.__name__)
            return res

        return _wrapper

    return wrapper
