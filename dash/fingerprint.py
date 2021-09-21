import re
from typing import Tuple

cache_regex = re.compile(r"^v[\w-]+m[0-9a-fA-F]+$")
version_clean = re.compile(r"[^\w-]")


def build_fingerprint(path: str, version: str, hash_value: str) -> str:
    path_parts = path.split("/")
    filename, extension = path_parts[-1].split(".", 1)

    return "{}.v{}m{}.{}".format(
        "/".join(path_parts[:-1] + [filename]),
        re.sub(version_clean, "_", str(version)),
        hash_value,
        extension,
    )


def check_fingerprint(path: str) -> Tuple[str, bool]:
    path_parts = path.split("/")
    name_parts = path_parts[-1].split(".")

    # Check if the resource has a fingerprint
    if len(name_parts) > 2 and cache_regex.match(name_parts[1]):
        original_name = ".".join([name_parts[0]] + name_parts[2:])
        return "/".join(path_parts[:-1] + [original_name]), True

    return path, False
