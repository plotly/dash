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
import inspect
from html import escape
from functools import wraps
from typing import Union
from dash.types import RendererHooks

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


def format_tag(
    tag_name, attributes, inner="", closed=False, opened=False, sanitize=False
):
    attributes = " ".join(
        [f'{k}="{escape(v) if sanitize else v}"' for k, v in attributes.items()]
    )
    tag = f"<{tag_name} {attributes}"
    if closed:
        tag += "/>"
    elif opened:
        tag += ">"
    else:
        tag += ">" + inner + f"</{tag_name}>"
    return tag


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
        if not names:
            return next(iter(self), {})


def create_callback_id(output, inputs, no_output=False):
    # A single dot within a dict id key or value is OK
    # but in case of multiple dots together escape each dot
    # with `\` so we don't mistake it for multi-outputs
    hashed_inputs = None

    def _hash_inputs():
        return hashlib.sha256(
            ".".join(str(x) for x in inputs).encode("utf-8")
        ).hexdigest()

    def _concat(x):
        nonlocal hashed_inputs
        _id = x.component_id_str().replace(".", "\\.") + "." + x.component_property
        if x.allow_duplicate:
            if not hashed_inputs:
                hashed_inputs = _hash_inputs()
            # Actually adds on the property part.
            _id += f"@{hashed_inputs}"
        return _id

    if no_output:
        # No output will hash the inputs.
        return _hash_inputs()

    if isinstance(output, (list, tuple)):
        return ".." + "...".join(_concat(x) for x in output) + ".."

    return _concat(output)


# inverse of create_callback_id - should only be relevant if an old renderer is
# hooked up to a new back end, which will only happen in special cases like
# embedded
def split_callback_id(callback_id):
    if callback_id.startswith(".."):
        return [split_callback_id(oi) for oi in callback_id[2:-2].split("...")]

    id_, prop = callback_id.rsplit(".", 1)
    return {"id": id_, "property": prop}


def stringify_id(id_):
    def _json(k, v):
        vstr = v.to_json() if hasattr(v, "to_json") else json.dumps(v)
        return f"{json.dumps(k)}:{vstr}"

    if isinstance(id_, dict):
        return "{" + ",".join(_json(k, id_[k]) for k in sorted(id_)) + "}"
    return id_


def inputs_to_dict(inputs_list):
    inputs = AttributeDict()
    for i in inputs_list:
        inputsi = i if isinstance(i, list) else [i]
        for ii in inputsi:
            id_str = stringify_id(ii["id"])
            inputs[f'{id_str}.{ii["property"]}'] = ii.get("value")
    return inputs


def convert_to_AttributeDict(nested_list):
    new_dict = []
    for i in nested_list:
        if isinstance(i, dict):
            new_dict.append(AttributeDict(i))
        else:
            new_dict.append([AttributeDict(ii) for ii in i])
    return new_dict


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


def compute_hash(path):
    with io.open(path, encoding="utf-8") as fp:
        return hashlib.sha256(fp.read().encode("utf-8")).hexdigest()


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


class OrderedSet(collections.abc.MutableSet):
    def __init__(self, *args):
        self._data = []
        for i in args:
            self.add(i)

    def add(self, value):
        if value not in self._data:
            self._data.append(value)

    def discard(self, value):
        self._data.remove(value)

    def __contains__(self, x):
        return x in self._data

    def __len__(self):
        return len(self._data)

    def __iter__(self):
        for i in self._data:
            yield i


def coerce_to_list(obj):
    if not isinstance(obj, (list, tuple)):
        return [obj]
    return obj


def clean_property_name(name: str):
    return name.split("@")[0]


def hooks_to_js_object(hooks: Union[RendererHooks, None]) -> str:
    if hooks is None:
        return ""
    hook_str = ",".join(f"{key}: {val}" for key, val in hooks.items())

    return f"{{{hook_str}}}"


def parse_version(version):
    return tuple(int(s) for s in version.split("."))


def get_caller_name():
    stack = inspect.stack()
    for s in stack:
        if s.function == "<module>":
            return s.frame.f_locals.get("__name__", "__main__")

    return "__main__"
