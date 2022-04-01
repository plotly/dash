# -*- coding: utf-8 -*-
import shlex
import sys
import uuid
import hashlib
import collections
import subprocess
import logging
import io
import json
import secrets
import string
from functools import wraps

logger = logging.getLogger()


def to_json(value):
    # pylint: disable=import-outside-toplevel
    from plotly.io.json import to_json_plotly

    return to_json_plotly(value)


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
        attributes=" ".join(['{}="{}"'.format(k, v) for k, v in attributes.items()]),
    )


def generate_hash():
    return str(uuid.uuid4().hex).strip("-")


# pylint: disable=no-member
def patch_collections_abc(member):
    return getattr(collections.abc, member)


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
        """
        Designate named attributes as read-only with the corresponding msg

        Method is additive. Making additional calls to this method will update
        existing messages and add to the current set of _read_only names.
        """
        new_read_only = {name: msg for name in names}
        if getattr(self, "_read_only", False):
            self._read_only.update(new_read_only)
        else:
            object.__setattr__(self, "_read_only", new_read_only)

    def finalize(self, msg="Object is final: No new keys may be added."):
        """Prevent any new keys being set."""
        object.__setattr__(self, "_final", msg)

    def __setitem__(self, key, val):
        if key in self.__dict__.get("_read_only", {}):
            raise AttributeError(self._read_only[key], key)

        final_msg = self.__dict__.get("_final")
        if final_msg and key not in self:
            raise AttributeError(final_msg, key)

        return super().__setitem__(key, val)

    def update(self, other):
        # Overrides dict.update() to use __setitem__ above
        for k, v in other.items():
            self[k] = v

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
                "{}.{}".format(
                    # A single dot within a dict id key or value is OK
                    # but in case of multiple dots together escape each dot
                    # with `\` so we don't mistake it for multi-outputs
                    x.component_id_str().replace(".", "\\."),
                    x.component_property,
                )
                for x in output
            )
        )

    return "{}.{}".format(
        output.component_id_str().replace(".", "\\."), output.component_property
    )


# inverse of create_callback_id - should only be relevant if an old renderer is
# hooked up to a new back end, which will only happen in special cases like
# embedded
def split_callback_id(callback_id):
    if callback_id.startswith(".."):
        return [split_callback_id(oi) for oi in callback_id[2:-2].split("...")]

    id_, prop = callback_id.rsplit(".", 1)
    return {"id": id_, "property": prop}


def stringify_id(id_):
    if isinstance(id_, dict):
        return json.dumps(id_, sort_keys=True, separators=(",", ":"))
    return id_


def inputs_to_dict(inputs_list):
    inputs = {}
    for i in inputs_list:
        inputsi = i if isinstance(i, list) else [i]
        for ii in inputsi:
            id_str = stringify_id(ii["id"])
            inputs["{}.{}".format(id_str, ii["property"])] = ii.get("value")
    return inputs


def inputs_to_vals(inputs):
    return [
        [ii.get("value") for ii in i] if isinstance(i, list) else i.get("value")
        for i in inputs
    ]


def run_command_with_process(cmd):
    is_win = sys.platform == "win32"
    with subprocess.Popen(shlex.split(cmd, posix=is_win), shell=is_win) as proc:
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
    with io.open(path, encoding="utf-8") as fp:
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


def gen_salt(chars):
    return "".join(
        secrets.choice(string.ascii_letters + string.digits) for _ in range(chars)
    )
