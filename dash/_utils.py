# -*- coding: utf-8 -*-
import shlex
import sys
import uuid
import hashlib
import importlib
from collections import abc
import subprocess
import logging
import io
import json
import secrets
import string
import inspect
import re
import os

from html import escape
from functools import wraps
from typing import Union
from .types import RendererHooks

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
    return getattr(abc, member)


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

    def unset_read_only(self, keys):
        if hasattr(self, "_read_only"):
            for key in keys:
                self._read_only.pop(key, None)

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

    def update(self, other=None, **kwargs):
        # Overrides dict.update() to use __setitem__ above
        # Needs default `None` and `kwargs` to satisfy type checking
        source = other if other is not None else kwargs
        for k, v in source.items():
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


def stringify_id(id_) -> str:
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


class OrderedSet(abc.MutableSet):
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


def pascal_case(name: Union[str, None]):
    s = re.sub(r"\s", "_", str(name))
    # Replace leading `_`
    s = re.sub("^[_]+", "", s)
    if not s:
        return s
    return s[0].upper() + re.sub(
        r"[\-_\.]+([a-z])", lambda match: match.group(1).upper(), s[1:]
    )


def get_root_path(import_name: str) -> str:
    """Find the root path of a package, or the path that contains a
    module. If it cannot be found, returns the current working
    directory.

    Not to be confused with the value returned by :func:`find_package`.

    :meta private:
    """
    # Module already imported and has a file attribute. Use that first.
    mod = sys.modules.get(import_name)

    if mod is not None and hasattr(mod, "__file__") and mod.__file__ is not None:
        return os.path.dirname(os.path.abspath(mod.__file__))

    # Next attempt: check the loader.
    try:
        spec = importlib.util.find_spec(import_name)

        if spec is None:
            raise ValueError
    except (ImportError, ValueError):
        loader = None
    else:
        loader = spec.loader

    # Loader does not exist or we're referring to an unloaded main
    # module or a main module without path (interactive sessions), go
    # with the current working directory.
    if loader is None:
        return os.getcwd()

    if hasattr(loader, "get_filename"):
        filepath = loader.get_filename(import_name)  # pyright: ignore
    else:
        # Fall back to imports.
        __import__(import_name)
        mod = sys.modules[import_name]
        filepath = getattr(mod, "__file__", None)

        # If we don't have a file path it might be because it is a
        # namespace package. In this case pick the root path from the
        # first module that is contained in the package.
        if filepath is None:
            raise RuntimeError(
                "No root path can be found for the provided module"
                f" {import_name!r}. This can happen because the module"
                " came from an import hook that does not provide file"
                " name information or because it's a namespace package."
                " In this case the root path needs to be explicitly"
                " provided."
            )

    # filepath is import_name.py for a module, or __init__.py for a package.
    return os.path.dirname(os.path.abspath(filepath))  # type: ignore[no-any-return]
